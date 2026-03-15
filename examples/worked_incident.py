"""Worked instantiation -- §III-D of the paper, as a real execution trace.

Replays the two-alert payments-service incident through the actual
``TierController``/``Incident`` machinery and emits the console trace plus a
JSON audit log. The numbers reported in §III-D of the paper are taken directly
from this program's output, so paper and artifact cannot drift apart.

Run:
    python -m examples.worked_incident
"""
from __future__ import annotations

import json
from pathlib import Path

from tiered_autonomy.controller import TierController
from tiered_autonomy.incident import Incident
from tiered_autonomy.taxonomy import ReversibilityPolicy
from tiered_autonomy.types import Action


def build_incident() -> Incident:
    """Construct and run the §III-D payments-service incident."""
    policy = ReversibilityPolicy.load()
    controller = TierController(policy)
    incident = Incident(controller, incident_id="payments-latency-2026")

    # Alert 1: a latency alert; the agent is highly confident the cause is a
    # recently deployed canary. Rolling it back is cheap and reversible (R2).
    incident.step(
        Action("roll back the canary in the staging namespace"),
        confidence=0.91,
        outcome="rollback succeeded; metrics recovered",
    )

    # Alert 2 (minutes later): error rates rise on a downstream consumer; the
    # diagnosis now splits across two hypotheses. The proposed action -- rotate
    # the service-account credential -- is hard to reverse and cross-tenant (R4).
    incident.step(
        Action("rotate the service account credential"),
        confidence=0.62,
        outcome="escalated; operator selected the alternative hypothesis",
    )

    return incident


def main() -> dict:
    incident = build_incident()

    print("=" * 74)
    print(f"WORKED INSTANTIATION (§III-D)  --  incident: {incident.incident_id}")
    print("=" * 74)
    for i, d in enumerate(incident.decisions, start=1):
        verdict = "ACTS autonomously" if d.autonomous else "ESCALATES to human"
        triggers = ", ".join(t.value for t in d.triggers) or "none"
        print(f"\nAlert {i}: {d.action.name}")
        print(f"  class={d.reversibility_class.name}  confidence={d.confidence:.2f}  "
              f"threshold={'n/a' if d.threshold is None else f'{d.threshold:.2f}'}")
        print(f"  -> tier {d.tier.name} ({d.tier.label})")
        print(f"  -> {verdict}   triggers: {triggers}")
        print(f"  rationale: {d.rationale}")

    print("\n" + "-" * 74)
    print("SUMMARY:", json.dumps(incident.summary(), indent=None))

    out_dir = Path(__file__).resolve().parent.parent / "figures"
    out_dir.mkdir(exist_ok=True)
    audit_path = out_dir / "worked_incident_audit.json"
    incident.audit_log.to_json(str(audit_path))
    print(f"Audit log written to {audit_path}")

    return {
        "summary": incident.summary(),
        "decisions": [d.to_dict() for d in incident.decisions],
    }


if __name__ == "__main__":
    main()
