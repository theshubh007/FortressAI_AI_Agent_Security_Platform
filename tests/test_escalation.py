"""Unit tests for the pure evaluate_triggers helper."""
from __future__ import annotations

import pytest

from tiered_autonomy.escalation import evaluate_triggers
from tiered_autonomy.taxonomy import ReversibilityPolicy
from tiered_autonomy.types import (
    Action,
    EscalationTrigger,
    ReversibilityClass,
    Tier,
)


@pytest.fixture(scope="module")
def policy():
    return ReversibilityPolicy.load()


def _triggers(policy, name, rclass, conf, override=None, precondition_ok=True):
    action = Action(name, precondition_ok=precondition_ok)
    threshold = policy.threshold(rclass) if rclass is not None else None
    return evaluate_triggers(action, rclass, conf, threshold, policy, override)


def test_operator_override_dominates(policy):
    t = _triggers(policy, "metrics query", ReversibilityClass.R1, 0.9,
                  override=Tier.T1)
    assert t == [EscalationTrigger.OPERATOR_OVERRIDE]


def test_override_beats_unclassified_and_r5(policy):
    assert _triggers(policy, "frobnicate", None, 0.9, override=Tier.T2) == [
        EscalationTrigger.OPERATOR_OVERRIDE
    ]
    assert _triggers(policy, "delete", ReversibilityClass.R5, 0.9,
                     override=Tier.T2) == [EscalationTrigger.OPERATOR_OVERRIDE]


def test_unclassified(policy):
    assert _triggers(policy, "frobnicate", None, 0.9) == [
        EscalationTrigger.UNCLASSIFIED_ACTION
    ]


def test_never_autonomous_r5(policy):
    assert _triggers(policy, "delete", ReversibilityClass.R5, 1.0) == [
        EscalationTrigger.BLAST_RADIUS_CEILING
    ]


def test_r5_dominates_precondition(policy):
    """R5 ceiling is checked before precondition mismatch."""
    t = _triggers(policy, "delete", ReversibilityClass.R5, 0.1,
                  precondition_ok=False)
    assert t == [EscalationTrigger.BLAST_RADIUS_CEILING]


def test_precondition_mismatch(policy):
    t = _triggers(policy, "cache warm", ReversibilityClass.R2, 0.99,
                  precondition_ok=False)
    assert t == [EscalationTrigger.PRECONDITION_MISMATCH]


def test_precondition_dominates_confidence(policy):
    """Broken precondition escalates even when confidence is below gate."""
    t = _triggers(policy, "cache warm", ReversibilityClass.R2, 0.1,
                  precondition_ok=False)
    assert t == [EscalationTrigger.PRECONDITION_MISMATCH]


def test_confidence_below_threshold(policy):
    t = _triggers(policy, "credential rotate", ReversibilityClass.R4, 0.62)
    assert t == [EscalationTrigger.CONFIDENCE_BELOW_THRESHOLD]


def test_confidence_at_threshold_no_trigger(policy):
    """Exactly at threshold clears the gate (>=)."""
    assert _triggers(policy, "canary rollback", ReversibilityClass.R2, 0.80) == []


def test_confidence_above_threshold_no_trigger(policy):
    assert _triggers(policy, "canary rollback", ReversibilityClass.R2, 0.95) == []


def test_always_autonomous_no_trigger(policy):
    assert _triggers(policy, "metrics query", ReversibilityClass.R1, 0.01) == []


def test_returns_list(policy):
    assert isinstance(
        _triggers(policy, "metrics query", ReversibilityClass.R1, 0.9), list
    )
