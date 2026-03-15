"""Incident timeline -- bidirectional authority transitions over time.

An ``Incident`` drives a sequence of decisions through a single
``TierController`` and records each one in an ``AuditLog``. The key property it
demonstrates (§III of the paper) is that authority is *bidirectional*: the
controller can move the agent UP the ladder (toward autonomy) as confidence and
reversibility permit, and back DOWN (toward the human) when an escalation
trigger fires -- all within one incident.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from .audit import AuditLog
from .controller import TierController
from .types import Action, AuditRecord, Decision, Tier


class Incident:
    """A live incident: an ordered series of controller decisions."""

    def __init__(self, controller: TierController, incident_id: str = "incident-0001"):
        self.controller = controller
        self.incident_id = incident_id
        self.audit_log = AuditLog()
        self.tier_history: List[Tier] = []
        self.decisions: List[Decision] = []
        self._seq = 0

    # -- driving the timeline ----------------------------------------------
    def step(
        self,
        action: Action,
        confidence: float,
        operator_override: Optional[Tier] = None,
        outcome: Optional[str] = None,
    ) -> Decision:
        """Decide on one action, record it, and advance the timeline."""
        decision = self.controller.decide(
            action, confidence, operator_override=operator_override
        )
        timestamp = datetime.now(timezone.utc).isoformat()
        record = AuditRecord.from_decision(
            seq=self._seq,
            timestamp=timestamp,
            decision=decision,
            outcome=outcome,
        )
        self.audit_log.append(record)
        self.tier_history.append(decision.tier)
        self.decisions.append(decision)
        self._seq += 1
        return decision

    # -- reporting ----------------------------------------------------------
    def summary(self) -> Dict[str, object]:
        """Return aggregate counts describing the incident so far."""
        autonomous_count = sum(1 for d in self.decisions if d.autonomous)
        escalation_count = sum(1 for d in self.decisions if d.triggers)
        tiers_visited = sorted(
            {t.name for t in self.tier_history}
        )
        return {
            "incident_id": self.incident_id,
            "steps": len(self.decisions),
            "autonomous_count": autonomous_count,
            "escalation_count": escalation_count,
            "tiers_visited": tiers_visited,
            "tier_history": [t.name for t in self.tier_history],
        }
