"""Pins the §III-D worked-instantiation trace to the values used in the paper.

If the controller logic or the policy thresholds ever change such that the
paper's narrative no longer holds, this test fails -- keeping the paper and the
artifact in lockstep.
"""
from examples.worked_incident import build_incident
from tiered_autonomy.types import EscalationTrigger, ReversibilityClass, Tier


def test_worked_incident_matches_paper_trace():
    incident = build_incident()
    d1, d2 = incident.decisions

    # Alert 1: canary rollback -- reversible (R2), confident -> acts at T4.
    assert d1.reversibility_class is ReversibilityClass.R2
    assert d1.confidence == 0.91
    assert d1.threshold == 0.80
    assert d1.tier is Tier.T4
    assert d1.autonomous is True
    assert d1.triggers == []

    # Alert 2: credential rotation -- hard to reverse (R4), low confidence ->
    # demotes to T2 and escalates to the operator.
    assert d2.reversibility_class is ReversibilityClass.R4
    assert d2.confidence == 0.62
    assert d2.threshold == 0.95
    assert d2.tier is Tier.T2
    assert d2.autonomous is False
    assert EscalationTrigger.CONFIDENCE_BELOW_THRESHOLD in d2.triggers


def test_authority_moves_within_one_incident():
    incident = build_incident()
    summary = incident.summary()
    # Authority moved: one autonomous action, one escalation, two distinct tiers.
    assert summary["autonomous_count"] == 1
    assert summary["escalation_count"] == 1
    assert summary["tier_history"] == ["T4", "T2"]
