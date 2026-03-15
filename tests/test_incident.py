"""Tests for the Incident timeline and its bidirectional transitions."""
from __future__ import annotations

import json

import pytest

from tiered_autonomy.controller import TierController
from tiered_autonomy.incident import Incident
from tiered_autonomy.taxonomy import ReversibilityPolicy
from tiered_autonomy.types import Action, Tier


@pytest.fixture(scope="module")
def policy():
    return ReversibilityPolicy.load()


@pytest.fixture()
def incident(policy):
    return Incident(TierController(policy), incident_id="inc-test")


def test_step_records_and_returns_decision(incident):
    d = incident.step(Action("metrics query for latency"), 0.9, outcome="ok")
    assert d.tier is Tier.T5
    assert len(incident.audit_log) == 1
    rec = incident.audit_log.records[0]
    assert rec.seq == 0
    assert rec.action_name == "metrics query for latency"
    assert rec.outcome == "ok"
    assert rec.timestamp.endswith("+00:00")  # ISO-8601 UTC


def test_bidirectional_authority_up_and_down(incident):
    """Authority moves UP (T5) then DOWN (T2) then UP again within one incident."""
    # Step 0: read-only, fully autonomous (T5).
    incident.step(Action("metrics query for latency"), 0.9)
    # Step 1: unclassified action -> down to Advise (T2).
    incident.step(Action("frobnicate the widget"), 0.9)
    # Step 2: confident R2 rollback -> up to Bounded Autonomy (T4).
    incident.step(Action("roll back the canary in staging"), 0.95)
    # Step 3: R4 below gate -> down to Advise (T2).
    incident.step(Action("rotate the service account credential"), 0.5)
    # Step 4: R4 above gate -> up to Execute-then-Review (T3).
    incident.step(Action("rotate the service account credential"), 0.97)

    tiers = [t.name for t in incident.tier_history]
    assert tiers == ["T5", "T2", "T4", "T2", "T3"]

    # Explicit up- and down-transitions present.
    deltas = [
        incident.tier_history[i + 1].value - incident.tier_history[i].value
        for i in range(len(incident.tier_history) - 1)
    ]
    assert any(d > 0 for d in deltas), "expected at least one up-transition"
    assert any(d < 0 for d in deltas), "expected at least one down-transition"


def test_operator_override_step(incident):
    d = incident.step(
        Action("roll back the canary in staging"), 0.99,
        operator_override=Tier.T1,
    )
    assert d.tier is Tier.T1
    assert d.autonomous is False


def test_summary_counts(incident):
    incident.step(Action("metrics query for latency"), 0.9)          # T5 auto
    incident.step(Action("frobnicate the widget"), 0.9)              # T2 escalate
    incident.step(Action("roll back the canary in staging"), 0.95)  # T4 auto
    incident.step(Action("destructive delete of prod db"), 0.99)    # T1 escalate

    s = incident.summary()
    assert s["steps"] == 4
    assert s["autonomous_count"] == 2
    assert s["escalation_count"] == 2
    assert set(s["tiers_visited"]) == {"T1", "T2", "T4", "T5"}
    assert s["incident_id"] == "inc-test"


def test_audit_log_to_json(incident, tmp_path):
    incident.step(Action("metrics query for latency"), 0.9, outcome="clean")
    incident.step(Action("roll back the canary in staging"), 0.95, outcome="done")

    text = incident.audit_log.to_json()
    parsed = json.loads(text)
    assert len(parsed) == 2
    assert parsed[0]["action_name"] == "metrics query for latency"
    assert parsed[0]["outcome"] == "clean"
    assert parsed[1]["tier"] == "T4"

    # Writes to disk when a path is given.
    out = tmp_path / "audit.json"
    incident.audit_log.to_json(str(out))
    assert out.exists()
    assert json.loads(out.read_text())[0]["seq"] == 0
