"""The tiered-autonomy controller -- the core cybernetic decision loop.

``TierController.decide`` is the supervisory-control regulator of the paper: it
maps an (action, calibrated confidence) pair onto a tier of the five-tier
ladder and an autonomy verdict, using the reversibility policy as the
blast-radius envelope and the escalation triggers as the authority-transfer
mechanism.

The decision is *lexicographic* over safety (see ``escalation.evaluate_triggers``
for the ordering): human takeover, then unclassified/unbounded blast radius,
then precondition mismatch, and only last the calibrated-confidence gate.
"""
from __future__ import annotations

from typing import Callable, List, Optional

from .escalation import evaluate_triggers
from .taxonomy import ReversibilityPolicy
from .types import (
    Action,
    Decision,
    EscalationTrigger,
    ReversibilityClass,
    Tier,
)


class TierController:
    """Maps (action, confidence) -> Decision using the reversibility policy."""

    def __init__(
        self,
        policy: ReversibilityPolicy,
        calibrator: Optional[Callable[[float], float]] = None,
    ):
        self.policy = policy
        self.calibrator = calibrator

    # -- public API ---------------------------------------------------------
    def decide(
        self,
        action: Action,
        confidence: float,
        operator_override: Optional[Tier] = None,
    ) -> Decision:
        """Return the controller's verdict for ``action`` at ``confidence``.

        If a calibrator is configured the raw confidence is first mapped to a
        calibrated value; that calibrated value is what gates autonomy and is
        recorded in the returned ``Decision``.
        """
        # 1. Calibrate raw -> calibrated confidence.
        calibrated = confidence
        if self.calibrator is not None:
            calibrated = float(self.calibrator(confidence))

        # 2. Classify the action's reversibility (None == unclassified).
        rclass = self.policy.classify(action)
        threshold = self.policy.threshold(rclass) if rclass is not None else None

        # 3. Evaluate escalation triggers (the pure authority-transfer logic).
        triggers: List[EscalationTrigger] = evaluate_triggers(
            action=action,
            rclass=rclass,
            calibrated_confidence=calibrated,
            threshold=threshold,
            policy=self.policy,
            operator_override=operator_override,
        )

        # 4. Map the dominant trigger (or its absence) onto tier + autonomy.
        tier, autonomous, record_class = self._resolve(
            action=action,
            rclass=rclass,
            calibrated=calibrated,
            threshold=threshold,
            triggers=triggers,
            operator_override=operator_override,
        )

        rationale = self._rationale(
            action=action,
            record_class=record_class,
            classified=rclass is not None,
            calibrated=calibrated,
            threshold=threshold,
            tier=tier,
            autonomous=autonomous,
            triggers=triggers,
            operator_override=operator_override,
        )

        return Decision(
            action=action,
            reversibility_class=record_class,
            confidence=calibrated,
            threshold=threshold,
            tier=tier,
            autonomous=autonomous,
            triggers=triggers,
            rationale=rationale,
        )

    # -- internals ----------------------------------------------------------
    def _resolve(
        self,
        action: Action,
        rclass: Optional[ReversibilityClass],
        calibrated: float,
        threshold: Optional[float],
        triggers: List[EscalationTrigger],
        operator_override: Optional[Tier],
    ):
        """Return (tier, autonomous, reversibility_class_for_record)."""
        trigger = triggers[0] if triggers else None

        # 1. Operator override: human explicitly takes control at the given tier.
        if trigger is EscalationTrigger.OPERATOR_OVERRIDE:
            # Still record a class; unclassified is treated as maximally risky.
            record_class = rclass if rclass is not None else ReversibilityClass.R5
            return operator_override, False, record_class

        # 2. Unclassified: treat as maximally cautious (R5) but advise (T2).
        if trigger is EscalationTrigger.UNCLASSIFIED_ACTION:
            return Tier.T2, False, ReversibilityClass.R5

        # 3. Never-autonomous (R5): authority stays with the human at the ceiling.
        if trigger is EscalationTrigger.BLAST_RADIUS_CEILING:
            return self.policy.tier_ceiling(rclass), False, rclass

        # 4. Precondition mismatch: drop to Advise for a human sanity check.
        if trigger is EscalationTrigger.PRECONDITION_MISMATCH:
            return Tier.T2, False, rclass

        # 5. Confidence below the gate: drop to Advise.
        if trigger is EscalationTrigger.CONFIDENCE_BELOW_THRESHOLD:
            return Tier.T2, False, rclass

        # 6. No escalation: agent acts autonomously up to the class ceiling.
        #    (Covers always-autonomous R1 and gated classes above threshold.)
        return self.policy.tier_ceiling(rclass), True, rclass

    @staticmethod
    def _rationale(
        action: Action,
        record_class: ReversibilityClass,
        classified: bool,
        calibrated: float,
        threshold: Optional[float],
        tier: Tier,
        autonomous: bool,
        triggers: List[EscalationTrigger],
        operator_override: Optional[Tier],
    ) -> str:
        conf_s = f"{calibrated:.3f}"
        thr_s = "n/a" if threshold is None else f"{threshold:.3f}"
        trigger = triggers[0] if triggers else None

        if trigger is EscalationTrigger.OPERATOR_OVERRIDE:
            return (
                f"Operator override to {operator_override.name}: human takes "
                f"control of '{action.name}' (class {record_class.name}, "
                f"confidence {conf_s}); authority is not delegated."
            )
        if trigger is EscalationTrigger.UNCLASSIFIED_ACTION:
            return (
                f"Action '{action.name}' is unclassified; treated as maximally "
                f"risky ({record_class.name}) and held at {tier.name} (Advise) "
                f"for human classification. Confidence {conf_s} does not apply."
            )
        if trigger is EscalationTrigger.BLAST_RADIUS_CEILING:
            return (
                f"Class {record_class.name} is never-autonomous (unbounded, "
                f"non-recoverable blast radius); authority stays with the human "
                f"at the ceiling {tier.name} regardless of confidence "
                f"({conf_s})."
            )
        if trigger is EscalationTrigger.PRECONDITION_MISMATCH:
            return (
                f"Precondition mismatch for '{action.name}' (class "
                f"{record_class.name}); agent's mental model may be stale, so "
                f"drop to {tier.name} (Advise) despite confidence {conf_s} "
                f"vs threshold {thr_s}."
            )
        if trigger is EscalationTrigger.CONFIDENCE_BELOW_THRESHOLD:
            return (
                f"Calibrated confidence {conf_s} is below the {record_class.name} "
                f"gate ({thr_s}); drop to {tier.name} (Advise) rather than act "
                f"autonomously."
            )
        # No trigger: autonomous.
        if threshold is None:
            return (
                f"Class {record_class.name} is always-autonomous (no confidence "
                f"gate); agent acts autonomously at ceiling {tier.name} "
                f"(confidence {conf_s})."
            )
        return (
            f"Calibrated confidence {conf_s} clears the {record_class.name} gate "
            f"({thr_s}); agent acts autonomously at ceiling {tier.name}."
        )
