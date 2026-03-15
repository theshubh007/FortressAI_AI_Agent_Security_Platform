"""Shared types for the tiered-autonomy reference implementation.

These dataclasses/enums are the contract the controller, calibration,
simulator, and security modules all build against. Kept dependency-free.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class Tier(Enum):
    """The five-tier autonomy ladder (Fig. 1 of the paper).

    Higher value = more authority delegated to the agent.
    """
    T1 = 1  # Monitor           -- human in full control
    T2 = 2  # Advise            -- human acts on recommendation
    T3 = 3  # Execute-then-Review -- agent acts, post-hoc audit
    T4 = 4  # Bounded Autonomy  -- agent acts within envelope
    T5 = 5  # Full Autonomy     -- agent acts, no review

    @property
    def label(self) -> str:
        return {
            Tier.T1: "Monitor (human in full control)",
            Tier.T2: "Advise (human acts on recommendation)",
            Tier.T3: "Execute-then-Review (post-hoc audit)",
            Tier.T4: "Bounded Autonomy (agent acts within envelope)",
            Tier.T5: "Full Autonomy (agent acts, no review)",
        }[self]

    @property
    def is_autonomous(self) -> bool:
        """Tiers at which the agent executes without prior human sign-off."""
        return self in (Tier.T3, Tier.T4, Tier.T5)


class ReversibilityClass(Enum):
    """Blast-radius / reversibility classes (Table I of the paper)."""
    R1 = 1  # None; no state change
    R2 = 2  # Single service; seconds to undo
    R3 = 3  # Service group; minutes to undo
    R4 = 4  # Cross-service / cross-tenant; hours
    R5 = 5  # Unbounded; non-recoverable


class EscalationTrigger(Enum):
    """Conditions that transfer authority toward the human (§III)."""
    CONFIDENCE_BELOW_THRESHOLD = "confidence_below_threshold"
    PRECONDITION_MISMATCH = "precondition_mismatch"
    OPERATOR_OVERRIDE = "operator_override"
    BLAST_RADIUS_CEILING = "blast_radius_ceiling"  # never-autonomous class (R5)
    UNCLASSIFIED_ACTION = "unclassified_action"


@dataclass
class Action:
    """An action the agent is considering.

    `reversibility` may be set explicitly; otherwise the policy classifier
    infers it from `name` via declarative rules.
    """
    name: str
    reversibility: Optional[ReversibilityClass] = None
    precondition_ok: bool = True   # False models a mental-model mismatch
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """The controller's per-action verdict."""
    action: Action
    reversibility_class: ReversibilityClass
    confidence: float
    threshold: Optional[float]
    tier: Tier
    autonomous: bool
    triggers: List[EscalationTrigger] = field(default_factory=list)
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action.name,
            "reversibility_class": self.reversibility_class.name,
            "confidence": round(self.confidence, 4),
            "threshold": self.threshold,
            "tier": self.tier.name,
            "autonomous": self.autonomous,
            "triggers": [t.value for t in self.triggers],
            "rationale": self.rationale,
        }


@dataclass
class AuditRecord:
    """Structured post-hoc audit entry -- the concrete form of the T3 log."""
    seq: int
    timestamp: str
    action_name: str
    reversibility_class: str
    confidence: float
    threshold: Optional[float]
    tier: str
    autonomous: bool
    triggers: List[str]
    rationale: str
    outcome: Optional[str] = None

    @classmethod
    def from_decision(cls, seq: int, timestamp: str, decision: Decision,
                      outcome: Optional[str] = None) -> "AuditRecord":
        return cls(
            seq=seq,
            timestamp=timestamp,
            action_name=decision.action.name,
            reversibility_class=decision.reversibility_class.name,
            confidence=round(decision.confidence, 4),
            threshold=decision.threshold,
            tier=decision.tier.name,
            autonomous=decision.autonomous,
            triggers=[t.value for t in decision.triggers],
            rationale=decision.rationale,
            outcome=outcome,
        )
