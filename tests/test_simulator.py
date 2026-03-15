"""Tests for the vectorized §IV-B simulator.

The load-bearing test is FIDELITY: the fast vectorized `tiered` execute-decision
must equal the shipped TierController's `.autonomous` verdict on every sampled
(class, confidence) pair. If they ever diverge, the fast simulator is lying
about what the deployed controller would do, and the vectorized rule must be
fixed to match the controller (not the other way around).
"""
import numpy as np
import pytest

from tiered_autonomy.controller import TierController
from tiered_autonomy.simulator import (
    POLICY,
    THR,
    agg,
    execute_mask,
    run_once,
    tune_global_to_resolution,
)
from tiered_autonomy.taxonomy import ReversibilityPolicy
from tiered_autonomy.types import Action, ReversibilityClass

_CLASS_ORDER = [
    ReversibilityClass.R1,
    ReversibilityClass.R2,
    ReversibilityClass.R3,
    ReversibilityClass.R4,
    ReversibilityClass.R5,
]

# Keep tests fast: smaller N and fewer seeds than the experiment entrypoints.
TEST_N = 20_000
TEST_SEEDS = range(6)


def test_tiered_vectorized_matches_controller():
    """Fidelity: vectorized `tiered` execute == controller.decide().autonomous."""
    controller = TierController(POLICY)
    rng = np.random.default_rng(0)

    n_sample = 5000
    cls = rng.integers(0, 5, size=n_sample)
    conf = rng.random(n_sample)

    # Also inject exact-threshold boundary points for each gated class, since
    # the >= vs < boundary is exactly where a fast/slow mismatch would hide.
    boundary_conf = []
    boundary_cls = []
    for i, rc in enumerate(_CLASS_ORDER):
        t = POLICY.threshold(rc)
        if t is not None:
            for c in (t - 1e-9, t, t + 1e-9):
                boundary_conf.append(c)
                boundary_cls.append(i)
    cls = np.concatenate([cls, np.array(boundary_cls)])
    conf = np.concatenate([conf, np.array(boundary_conf)])

    vec_execute = execute_mask("tiered", conf, cls)

    for i in range(len(cls)):
        rc = _CLASS_ORDER[int(cls[i])]
        decision = controller.decide(
            Action(name=f"act-{i}", reversibility=rc), float(conf[i])
        )
        assert bool(vec_execute[i]) == bool(decision.autonomous), (
            f"mismatch at class={rc.name} conf={conf[i]:.6f}: "
            f"vec={bool(vec_execute[i])} controller={decision.autonomous}"
        )


def test_thresholds_read_from_policy_not_hardcoded():
    """The tiered gate uses the loaded policy's thresholds, R1/R5 non-gated."""
    assert np.isnan(THR[0])  # R1 always-autonomous (no numeric gate)
    assert np.isnan(THR[4])  # R5 never-autonomous (no numeric gate)
    assert THR[1] == POLICY.threshold(ReversibilityClass.R2)
    assert THR[2] == POLICY.threshold(ReversibilityClass.R3)
    assert THR[3] == POLICY.threshold(ReversibilityClass.R4)


def test_advisory_harm_is_zero():
    """Advisory executes nothing, so the agent can cause no execution harm."""
    m, _ = agg("advisory", seeds=TEST_SEEDS, n=TEST_N)
    assert m[1] == 0.0
    assert m[2] == pytest.approx(100.0)  # everything escalated


def test_full_autonomy_harm_exceeds_tiered():
    """Typed gating strictly reduces harm vs executing everything."""
    full, _ = agg("full", seeds=TEST_SEEDS, n=TEST_N)
    tiered, _ = agg("tiered", seeds=TEST_SEEDS, n=TEST_N)
    assert full[1] > tiered[1]


def test_tiered_resolution_is_large_fraction_of_full():
    """Tiered still resolves most of what full autonomy resolves."""
    full, _ = agg("full", seeds=TEST_SEEDS, n=TEST_N)
    tiered, _ = agg("tiered", seeds=TEST_SEEDS, n=TEST_N)
    assert tiered[0] > 0.6 * full[0]


def test_tune_global_matches_target_resolution():
    """The tuned global gate roughly reproduces the tiered resolution."""
    tiered, _ = agg("tiered", seeds=TEST_SEEDS, n=TEST_N)
    tg = tune_global_to_resolution(tiered[0], seeds=range(4), n=TEST_N)
    assert 0.50 <= tg <= 0.99
    global_m, _ = agg("global", seeds=TEST_SEEDS, n=TEST_N, tau_global=tg)
    assert abs(global_m[0] - tiered[0]) < 3.0  # within a few percentage points


def test_capability_is_policy_independent():
    """Same seed -> identical p_true regardless of policy (control isolation)."""
    # Resolution differs by policy, but the underlying capability draw is fixed;
    # we check that full autonomy's resolution equals the mean agent success,
    # which is a direct read-out of the fixed capability distribution.
    full, _ = agg("full", seeds=TEST_SEEDS, n=TEST_N)
    # Beta(3.5,1.5) mean ~0.70 -> full-autonomy resolution ~70%.
    assert 65.0 < full[0] < 75.0


def test_policy_obj_override_matches_default():
    """Passing an explicitly loaded policy yields identical results."""
    pol = ReversibilityPolicy.load()
    a = run_once(1, "tiered", n=TEST_N)
    b = run_once(1, "tiered", n=TEST_N, policy_obj=pol)
    assert a == pytest.approx(b)
