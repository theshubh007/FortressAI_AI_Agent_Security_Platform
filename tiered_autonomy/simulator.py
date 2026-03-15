"""Vectorized Monte-Carlo simulator for the §IV-B control-allocation study.

This module regenerates Table III of "Tiered Autonomy: A Human-Machine
Cybernetic Architecture for LLM-Based Incident Response" (IEEE SMC 2026).

Design intent (reviewer R1-1 / R1-6): isolate the *control-allocation*
variable from the *model-capability* variable. Agent capability -- the
per-action true success probability ``p_true`` -- is drawn from a FIXED
distribution (Beta(3.5, 1.5), mean ~0.70) and is IDENTICAL across every
policy. Only the allocation policy differs. The numbers this file prints are
an illustrative Monte-Carlo model under stated assumptions, NOT benchmark data.

Fidelity contract
-----------------
The vectorized ``tiered`` policy is a fast re-implementation of the shipped
:class:`tiered_autonomy.controller.TierController`. Its execute-decision MUST
equal ``TierController.decide(...).autonomous`` for every (class, confidence)
pair. ``tests/test_simulator.py`` asserts this on a random sample. The single
source of truth for the per-class thresholds and autonomy mode is the loaded
:class:`ReversibilityPolicy`; nothing here hardcodes threshold numbers.
"""
from __future__ import annotations

from typing import Dict, Iterable, Optional, Tuple

import numpy as np

from .taxonomy import ReversibilityPolicy
from .types import ReversibilityClass

# ---- Base generative assumptions (stated in the paper) --------------------
HARM = np.array([0.0, 1.0, 5.0, 25.0, 100.0])      # blast-radius cost, R1..R5
MIX = np.array([0.30, 0.35, 0.20, 0.10, 0.05])     # action-class mix, R1..R5
A_BETA, B_BETA = 3.5, 1.5     # capability: Beta mean ~0.70 (HELD FIXED)
SIGMA = 0.10                  # confidence noise
P_HUMAN = 0.85                # operator success on escalated actions
CAPACITY = 0.35               # operator bandwidth (fraction of stream)
N = 200_000

# Ordered R1..R5; index i (0..4) corresponds to class value i+1.
_CLASS_ORDER = [
    ReversibilityClass.R1,
    ReversibilityClass.R2,
    ReversibilityClass.R3,
    ReversibilityClass.R4,
    ReversibilityClass.R5,
]

# Load the shipped policy once -- the single source of truth for thresholds
# and per-class autonomy mode. Never hardcode threshold numbers here.
POLICY = ReversibilityPolicy.load()


def _policy_arrays(policy: ReversibilityPolicy = POLICY):
    """Derive (threshold, always_autonomous, never_autonomous) arrays.

    Indexed 0..4 for R1..R5, read straight from the loaded policy. For a class
    with no numeric threshold (R1 always, R5 never) the threshold slot is NaN;
    the vectorized rule masks those slots out, so a ``conf >= NaN`` (always
    False) comparison is never allowed to decide anything.
    """
    thr = np.full(5, np.nan)
    always = np.zeros(5, dtype=bool)
    never = np.zeros(5, dtype=bool)
    for i, rc in enumerate(_CLASS_ORDER):
        always[i] = policy.is_always_autonomous(rc)
        never[i] = policy.is_never_autonomous(rc)
        t = policy.threshold(rc)
        if t is not None:
            thr[i] = float(t)
    return thr, always, never


# Precomputed arrays for the default policy (fast path).
THR, ALWAYS, NEVER = _policy_arrays(POLICY)


def execute_mask(policy_name: str, conf: np.ndarray, cls: np.ndarray,
                 tau_global: float = 0.90,
                 thr: np.ndarray = THR, always: np.ndarray = ALWAYS,
                 never: np.ndarray = NEVER) -> np.ndarray:
    """Vectorized execute-decision (agent acts without a human) per action.

    Policies:
      * ``full``     -- execute every action.
      * ``advisory`` -- execute nothing (human acts on every recommendation).
      * ``global``   -- execute iff ``conf >= tau_global`` (one gate, all classes).
      * ``tiered``   -- mirror the shipped controller: R1 always, R5 never,
                        R2/R3/R4 iff ``conf >= threshold[class]``.
    """
    if policy_name == "full":
        return np.ones(conf.shape, dtype=bool)
    if policy_name == "advisory":
        return np.zeros(conf.shape, dtype=bool)
    if policy_name == "global":
        return conf >= tau_global
    if policy_name == "tiered":
        tau_vec = thr[cls]                     # NaN for always/never classes
        gated = ~always[cls] & ~never[cls]
        # NaN comparison is always False, so the `gated` mask is what actually
        # admits R2/R3/R4; R1 comes in via `always`, R5 is excluded by `never`.
        return always[cls] | (gated & (conf >= tau_vec))
    raise ValueError(f"unknown policy: {policy_name!r}")


def run_once(seed: int, policy: str, mix=MIX, harm=HARM, sigma=SIGMA,
             capacity=CAPACITY, p_human=P_HUMAN, bias: float = 0.0,
             tau_global: float = 0.90, n: int = N,
             poison_frac: float = 0.0, poison_conf: float = 1.0,
             policy_obj: Optional[ReversibilityPolicy] = None
             ) -> Tuple[float, float, float]:
    """One Monte-Carlo replicate. Returns (resolved%, harm/100, escalated%).

    Capability (``p_true``, hence ``agent_ok``) is drawn from the FIXED Beta
    distribution and is identical regardless of ``policy`` -- only the execute
    mask changes. ``bias`` models systematic overconfidence (confidence shifted
    up before clipping). ``poison_frac`` models telemetry-manipulation
    confidence poisoning (see :mod:`tiered_autonomy.security`): that fraction of
    actions has its confidence forced to ``poison_conf`` independent of truth.
    """
    harm = np.asarray(harm, dtype=np.float64)
    mix = np.asarray(mix, dtype=np.float64)

    if policy_obj is None or policy_obj is POLICY:
        thr, always, never = THR, ALWAYS, NEVER
    else:
        thr, always, never = _policy_arrays(policy_obj)

    rng = np.random.default_rng(seed)
    p_true = rng.beta(A_BETA, B_BETA, size=n)                    # capability (fixed)
    conf = np.clip(p_true + bias + rng.normal(0, sigma, n), 0, 1)  # +bias = overconfident
    agent_ok = rng.random(n) < p_true
    human_ok = rng.random(n) < p_human
    cls = rng.choice(5, size=n, p=mix)

    # Telemetry-manipulation poisoning: attacker inflates the agent's reported
    # confidence on the poisoned fraction, independent of true success.
    if poison_frac > 0.0:
        poisoned = rng.random(n) < poison_frac
        conf = conf.copy()
        conf[poisoned] = poison_conf

    execute = execute_mask(policy, conf, cls, tau_global=tau_global,
                           thr=thr, always=always, never=never)

    escalated = ~execute
    cap = int(capacity * n)
    esc_idx = np.flatnonzero(escalated)
    served = esc_idx[:cap]                        # overflow beyond cap = unresolved

    resolved = np.zeros(n, dtype=bool)
    resolved[execute] = agent_ok[execute]
    resolved[served] = human_ok[served]

    wrong_exec = execute & (~agent_ok)
    total_harm = harm[cls[wrong_exec]].sum()
    return 100 * resolved.mean(), 100 * total_harm / n, 100 * escalated.mean()


def agg(policy: str, seeds: Iterable[int] = range(40), **kw
        ) -> Tuple[np.ndarray, np.ndarray]:
    """Mean and 95% CI over seeds for (resolved%, harm/100, escalated%)."""
    r = np.array([run_once(s, policy, **kw) for s in seeds])
    m = r.mean(0)
    ci = 1.96 * r.std(0, ddof=1) / np.sqrt(len(r))
    return m, ci


def tune_global_to_resolution(target_res: float, seeds: Iterable[int] = range(5),
                              **kw) -> float:
    """Find the single global threshold whose resolution matches ``target_res``."""
    best_t, best_gap = 0.90, 1e9
    for t in np.linspace(0.50, 0.99, 50):
        m, _ = agg("global", seeds=seeds, tau_global=float(t), **kw)
        gap = abs(m[0] - target_res)
        if gap < best_gap:
            best_gap, best_t = gap, float(t)
    return best_t


def main() -> Dict[str, object]:
    """Print the 4-policy Table III comparison; return the numbers as a dict."""
    print("=" * 70)
    print("TABLE III -- CONTROL-ALLOCATION COMPARISON")
    print("(base config; capability held fixed; mean +/- 95% CI over 40 seeds)")
    print("=" * 70)
    tier_m, _ = agg("tiered")
    tg = tune_global_to_resolution(tier_m[0])   # global gate matched to tiered resolution
    print(f"(global-gate threshold tuned to match tiered resolution: tau_g={tg:.3f})\n")
    print(f"{'Policy':<16}{'Resolved %':>16}{'Harm/100':>16}{'Escalated %':>16}")

    rows: Dict[str, object] = {}
    for name, pol, kw in [("Full autonomy", "full", {}),
                          ("Advisory only", "advisory", {}),
                          ("Global gate", "global", {"tau_global": tg}),
                          ("Tiered (ours)", "tiered", {})]:
        m, ci = agg(pol, **kw)
        print(f"{name:<16}{m[0]:>10.1f}+/-{ci[0]:<4.1f}"
              f"{m[1]:>10.1f}+/-{ci[1]:<4.1f}{m[2]:>10.1f}+/-{ci[2]:<4.1f}")
        rows[pol] = {"name": name, "mean": m.tolist(), "ci": ci.tolist()}

    gm, _ = agg("global", tau_global=tg)
    tm, _ = agg("tiered")
    ratio = gm[1] / tm[1] if tm[1] > 0 else float("inf")
    print(f"\nAt matched resolution (~{tier_m[0]:.0f}%): tiered harm={tm[1]:.1f} "
          f"vs global-gate harm={gm[1]:.1f} -> typed gating cuts harm "
          f"{ratio:.1f}x further")

    rows["tau_global"] = tg
    rows["tiered_vs_global_harm_ratio"] = ratio
    return rows


if __name__ == "__main__":
    main()
