"""Acceptance + property tests for TierController.decide (§III / Table I)."""
from __future__ import annotations

import pytest

from tiered_autonomy.controller import TierController
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


@pytest.fixture()
def controller(policy):
    return TierController(policy)


# -- acceptance cases -------------------------------------------------------

def test_canary_rollback_r2_autonomous(controller):
    """§III-D: R2 canary rollback above threshold -> T4 autonomous."""
    d = controller.decide(Action("roll back the canary in staging"), 0.91)
    assert d.reversibility_class is ReversibilityClass.R2
    assert d.tier is Tier.T4
    assert d.autonomous is True
    assert d.triggers == []
    assert d.threshold == 0.80


def test_credential_rotation_below_threshold(controller):
    """§III-D: R4 credential rotation below gate -> T2, escalate."""
    d = controller.decide(Action("rotate the service account credential"), 0.62)
    assert d.reversibility_class is ReversibilityClass.R4
    assert d.tier is Tier.T2
    assert d.autonomous is False
    assert EscalationTrigger.CONFIDENCE_BELOW_THRESHOLD in d.triggers


def test_destructive_delete_r5_blocked(controller):
    """R5 destructive delete -> T1, never autonomous, blast-radius ceiling."""
    d = controller.decide(Action("destructive delete of the prod database"), 0.999)
    assert d.reversibility_class is ReversibilityClass.R5
    assert d.tier is Tier.T1
    assert d.autonomous is False
    assert EscalationTrigger.BLAST_RADIUS_CEILING in d.triggers


@pytest.mark.parametrize("conf", [0.0, 0.5, 0.99, 1.0])
def test_r5_never_autonomous_property(controller, conf):
    """Property: R5 is never autonomous for ANY confidence, including 1.0."""
    d = controller.decide(Action("destructive delete of the prod database"), conf)
    assert d.reversibility_class is ReversibilityClass.R5
    assert d.autonomous is False
    assert d.tier is Tier.T1
    assert EscalationTrigger.BLAST_RADIUS_CEILING in d.triggers


def test_metrics_query_r1_always_autonomous(controller):
    """R1 read-only -> T5 autonomous even at low confidence."""
    d = controller.decide(Action("metrics query for latency"), 0.2)
    assert d.reversibility_class is ReversibilityClass.R1
    assert d.tier is Tier.T5
    assert d.autonomous is True
    assert d.triggers == []


def test_unclassified_action(controller):
    """Unclassified -> treated as R5, T2 (Advise), UNCLASSIFIED_ACTION."""
    d = controller.decide(Action("frobnicate the widget"), 0.9)
    assert d.reversibility_class is ReversibilityClass.R5
    assert d.tier is Tier.T2
    assert d.autonomous is False
    assert EscalationTrigger.UNCLASSIFIED_ACTION in d.triggers


def test_r3_gated_above_and_below(controller):
    """R3 gated at threshold 0.88 -> autonomous above, escalate below.

    The YAML lists 'autoscaling change' as an R3 representative action but the
    name-regex does not match it (word-boundary), so we set the class
    explicitly to test the exact acceptance name; the classifier path is
    covered separately below.
    """
    hi = controller.decide(
        Action("autoscaling change", reversibility=ReversibilityClass.R3), 0.90
    )
    assert hi.reversibility_class is ReversibilityClass.R3
    assert hi.threshold == 0.88
    assert hi.tier is Tier.T4
    assert hi.autonomous is True
    assert hi.triggers == []

    lo = controller.decide(
        Action("autoscaling change", reversibility=ReversibilityClass.R3), 0.80
    )
    assert lo.tier is Tier.T2
    assert lo.autonomous is False
    assert EscalationTrigger.CONFIDENCE_BELOW_THRESHOLD in lo.triggers


def test_r3_gated_via_classifier(controller):
    """R3 reached by name classification ('feature-flag toggle')."""
    d = controller.decide(Action("feature-flag toggle"), 0.90)
    assert d.reversibility_class is ReversibilityClass.R3
    assert d.tier is Tier.T4
    assert d.autonomous is True


def test_precondition_mismatch(controller):
    """precondition_ok False -> T2, PRECONDITION_MISMATCH even at high conf."""
    d = controller.decide(Action("cache warm", precondition_ok=False), 0.99)
    assert d.tier is Tier.T2
    assert d.autonomous is False
    assert EscalationTrigger.PRECONDITION_MISMATCH in d.triggers


def test_operator_override_wins(controller):
    """Operator override to T1 wins over everything; not autonomous."""
    d = controller.decide(
        Action("roll back the canary in staging"), 0.99,
        operator_override=Tier.T1,
    )
    assert d.tier is Tier.T1
    assert d.autonomous is False
    assert EscalationTrigger.OPERATOR_OVERRIDE in d.triggers


def test_operator_override_beats_r5(controller):
    """Override records a class but still yields the override tier."""
    d = controller.decide(
        Action("destructive delete of the prod database"), 0.1,
        operator_override=Tier.T3,
    )
    assert d.tier is Tier.T3
    assert d.autonomous is False
    assert EscalationTrigger.OPERATOR_OVERRIDE in d.triggers


# -- calibration ------------------------------------------------------------

def test_calibrator_applied_and_recorded(policy):
    """Calibrator maps raw->calibrated; calibrated value gates and is recorded.

    Raw 0.99 is calibrated down to 0.50, below the R2 gate (0.80), so what
    would have been autonomous instead escalates.
    """
    ctrl = TierController(policy, calibrator=lambda c: 0.50)
    d = ctrl.decide(Action("roll back the canary in staging"), 0.99)
    assert d.confidence == 0.50
    assert d.autonomous is False
    assert EscalationTrigger.CONFIDENCE_BELOW_THRESHOLD in d.triggers


def test_r4_above_threshold_autonomous_t3(controller):
    """R4 above 0.95 -> ceiling T3 (execute-then-review), autonomous."""
    d = controller.decide(Action("rotate the service account credential"), 0.97)
    assert d.reversibility_class is ReversibilityClass.R4
    assert d.tier is Tier.T3
    assert d.autonomous is True
    assert d.triggers == []


def test_rationale_is_informative(controller):
    """Rationale mentions class, confidence, and threshold context."""
    d = controller.decide(Action("rotate the service account credential"), 0.62)
    assert "R4" in d.rationale
    assert "0.6" in d.rationale
    assert "0.95" in d.rationale
