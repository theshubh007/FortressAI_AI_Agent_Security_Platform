"""Escalation-trigger evaluation (the authority-transfer logic of §III).

The controller's decision is driven by a small, ordered set of *escalation
triggers* -- conditions that transfer authority from the agent toward the
human. This module factors that logic into one pure, side-effect-free helper
so it can be reasoned about and unit-tested in isolation.

The trigger priority order encodes the paper's safety lexicography: an explicit
human takeover dominates everything, an unclassified/unbounded blast radius
dominates confidence, a broken precondition (mental-model mismatch) dominates
the confidence gate, and only then does the calibrated-confidence gate apply.
"""
from __future__ import annotations

from typing import List, Optional

from .types import (
    Action,
    EscalationTrigger,
    ReversibilityClass,
    Tier,
)


def evaluate_triggers(
    action: Action,
    rclass: Optional[ReversibilityClass],
    calibrated_confidence: float,
    threshold: Optional[float],
    policy,
    operator_override: Optional[Tier] = None,
) -> List[EscalationTrigger]:
    """Return the escalation triggers that fire for this action.

    Pure function: no I/O, no mutation. At most one trigger fires -- the
    highest-priority applicable one -- returned as a single-element list. An
    empty list means "no escalation: the agent may act autonomously".

    Priority (highest first):
      1. OPERATOR_OVERRIDE       -- human explicitly takes control
      2. UNCLASSIFIED_ACTION     -- rclass is None (treated as maximally risky)
      3. BLAST_RADIUS_CEILING    -- never-autonomous class (R5)
      4. PRECONDITION_MISMATCH   -- action.precondition_ok is False
      5. CONFIDENCE_BELOW_THRESHOLD -- gated class, confidence < threshold
    """
    # 1. Human takeover wins over everything.
    if operator_override is not None:
        return [EscalationTrigger.OPERATOR_OVERRIDE]

    # 2. Unclassified action: no envelope known -> escalate.
    if rclass is None:
        return [EscalationTrigger.UNCLASSIFIED_ACTION]

    # 3. Never-autonomous (R5): blast radius unbounded regardless of confidence.
    if policy.is_never_autonomous(rclass):
        return [EscalationTrigger.BLAST_RADIUS_CEILING]

    # 4. Precondition / mental-model mismatch: agent's world-view is stale.
    if not action.precondition_ok:
        return [EscalationTrigger.PRECONDITION_MISMATCH]

    # 5. Always-autonomous (R1): no confidence gate.
    if policy.is_always_autonomous(rclass):
        return []

    # 6. Gated class (R2/R3/R4): confidence must clear the threshold.
    if threshold is not None and calibrated_confidence < threshold:
        return [EscalationTrigger.CONFIDENCE_BELOW_THRESHOLD]

    return []
