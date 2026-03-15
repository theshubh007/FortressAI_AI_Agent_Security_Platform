"""Blast radius as a containment primitive under adversarial confidence poisoning.

This module operationalizes the adversarial paragraph of §IV. The threat is
*telemetry-manipulation confidence poisoning* (cf. Qiu et al.; Pasquini et al.):
an attacker who can influence the signals the agent reasons over inflates the
agent's reported confidence on poisoned diagnoses -- driving confidence toward
~1.0 independent of whether the underlying action would actually succeed.

Against a purely confidence-gated defense, poisoning is devastating: every
poisoned action clears the gate and executes. The tiered architecture adds a
second, confidence-independent line of defense -- the *reversibility envelope*.
Because R5 (unbounded, non-recoverable blast radius) is NEVER autonomous, no
amount of confidence inflation can make the agent execute a catastrophic action.

Headline result demonstrated numerically by :func:`run_containment`:
    under tiered allocation, catastrophic (R5) harm stays exactly 0 even under
    maximal poisoning, while full autonomy's R5 harm explodes.
"""
from __future__ import annotations

from typing import Dict, Iterable, Optional

import numpy as np

from .simulator import (
    A_BETA,
    B_BETA,
    CAPACITY,
    HARM,
    MIX,
    N,
    P_HUMAN,
    POLICY,
    SIGMA,
    execute_mask,
    _policy_arrays,
)
from .taxonomy import ReversibilityPolicy
from .types import ReversibilityClass

# R5 is index 4 in the R1..R5 ordering; harm weight 100 (catastrophic).
_R5_INDEX = ReversibilityClass.R5.value - 1


def _run_poisoned(seed: int, policy: str, poison_frac: float,
                  poison_conf: float = 1.0, mix=MIX, harm=HARM, sigma=SIGMA,
                  capacity=CAPACITY, p_human=P_HUMAN, bias: float = 0.0,
                  tau_global: float = 0.90, n: int = N,
                  policy_obj: Optional[ReversibilityPolicy] = None):
    """One poisoned replicate. Returns (total_harm/100, r5_harm/100, resolved%).

    Capability (``p_true``) is drawn from the same FIXED Beta distribution as
    the benign simulator -- poisoning corrupts only the *reported confidence*,
    never the true success of the action.
    """
    harm = np.asarray(harm, dtype=np.float64)
    mix = np.asarray(mix, dtype=np.float64)

    if policy_obj is None or policy_obj is POLICY:
        thr, always, never = _policy_arrays(POLICY)
    else:
        thr, always, never = _policy_arrays(policy_obj)

    rng = np.random.default_rng(seed)
    p_true = rng.beta(A_BETA, B_BETA, size=n)
    conf = np.clip(p_true + bias + rng.normal(0, sigma, n), 0, 1)
    agent_ok = rng.random(n) < p_true
    human_ok = rng.random(n) < p_human
    cls = rng.choice(5, size=n, p=mix)

    # Attacker inflates confidence on the poisoned fraction, independent of truth.
    if poison_frac > 0.0:
        poisoned = rng.random(n) < poison_frac
        conf[poisoned] = poison_conf

    execute = execute_mask(policy, conf, cls, tau_global=tau_global,
                           thr=thr, always=always, never=never)

    escalated = ~execute
    cap = int(capacity * n)
    served = np.flatnonzero(escalated)[:cap]
    resolved = np.zeros(n, dtype=bool)
    resolved[execute] = agent_ok[execute]
    resolved[served] = human_ok[served]

    wrong_exec = execute & (~agent_ok)
    total_harm = harm[cls[wrong_exec]].sum()
    r5_wrong = wrong_exec & (cls == _R5_INDEX)
    r5_harm = harm[cls[r5_wrong]].sum()

    return (100 * total_harm / n, 100 * r5_harm / n, 100 * resolved.mean())


def _agg_poisoned(policy: str, poison_frac: float, seeds: Iterable[int],
                  **kw):
    r = np.array([_run_poisoned(s, policy, poison_frac, **kw) for s in seeds])
    return r.mean(0)


def run_containment(poison_frac: float = 1.0, seeds: Iterable[int] = range(40),
                    n: int = N, **kw) -> Dict[str, object]:
    """Compare full autonomy vs tiered under confidence poisoning.

    Parameters
    ----------
    poison_frac : float
        Fraction of actions whose confidence the attacker forces to ~1.0.
        ``1.0`` is maximal poisoning (every action's confidence is spoofed).
    seeds : iterable of int
        Monte-Carlo seeds to average over.

    Returns
    -------
    dict with total and catastrophic (R5) harm/100 for both policies, plus the
    key finding flag ``tiered_r5_contained`` (True iff tiered R5 harm == 0).
    """
    full = _agg_poisoned("full", poison_frac, seeds, n=n, **kw)
    tiered = _agg_poisoned("tiered", poison_frac, seeds, n=n, **kw)

    # Benign baseline (no poisoning) for context.
    full_benign = _agg_poisoned("full", 0.0, seeds, n=n, **kw)
    tiered_benign = _agg_poisoned("tiered", 0.0, seeds, n=n, **kw)

    result = {
        "poison_frac": poison_frac,
        "seeds": len(list(seeds)) if hasattr(seeds, "__len__") else None,
        "full_total_harm": float(full[0]),
        "full_r5_harm": float(full[1]),
        "full_resolved_pct": float(full[2]),
        "tiered_total_harm": float(tiered[0]),
        "tiered_r5_harm": float(tiered[1]),
        "tiered_resolved_pct": float(tiered[2]),
        "full_total_harm_benign": float(full_benign[0]),
        "full_r5_harm_benign": float(full_benign[1]),
        "tiered_total_harm_benign": float(tiered_benign[0]),
        "tiered_r5_harm_benign": float(tiered_benign[1]),
        "tiered_r5_contained": bool(tiered[1] == 0.0),
        "total_harm_reduction_x": (float(full[0] / tiered[0])
                                   if tiered[0] > 0 else float("inf")),
    }
    return result


def main() -> Dict[str, object]:
    """Print the full-vs-tiered containment comparison; return metrics dict."""
    res = run_containment(poison_frac=1.0)
    print("=" * 70)
    print("ADVERSARIAL CONTAINMENT -- confidence poisoning (maximal, frac=1.0)")
    print("(mean over 40 seeds; capability fixed; only reported confidence poisoned)")
    print("=" * 70)
    print(f"{'Policy':<16}{'Total harm/100':>18}{'R5 (catastrophic)':>20}")
    print(f"{'Full autonomy':<16}{res['full_total_harm']:>18.1f}"
          f"{res['full_r5_harm']:>20.1f}")
    print(f"{'Tiered (ours)':<16}{res['tiered_total_harm']:>18.1f}"
          f"{res['tiered_r5_harm']:>20.1f}")
    print(f"\nCatastrophic (R5) harm under tiered: {res['tiered_r5_harm']:.1f} "
          f"(contained={res['tiered_r5_contained']})")
    print(f"Total harm reduction (full/tiered): "
          f"{res['total_harm_reduction_x']:.1f}x")
    return res


if __name__ == "__main__":
    main()
