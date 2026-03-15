"""Structured post-hoc audit log -- the concrete form of the T3 record.

Every controller decision, whatever tier it lands on, is appended here as an
``AuditRecord``. This is what makes "Execute-then-Review" (T3) and "Bounded
Autonomy" (T4) auditable after the fact: a replayable, serializable trail of
what the agent decided, why (rationale + triggers), and how it turned out
(outcome).
"""
from __future__ import annotations

import json
from typing import List, Optional

from .types import AuditRecord


class AuditLog:
    """An append-only, serializable log of audit records."""

    def __init__(self) -> None:
        self.records: List[AuditRecord] = []

    def append(self, record: AuditRecord) -> None:
        """Append a single audit record to the log."""
        self.records.append(record)

    def __len__(self) -> int:
        return len(self.records)

    def __iter__(self):
        return iter(self.records)

    def to_json(self, path: Optional[str] = None) -> str:
        """Serialize the log to pretty JSON.

        Returns the JSON string. If ``path`` is given, also writes it there
        (UTF-8) before returning.
        """
        payload = [self._record_to_dict(r) for r in self.records]
        text = json.dumps(payload, indent=2, sort_keys=False)
        if path is not None:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(text)
        return text

    @staticmethod
    def _record_to_dict(record: AuditRecord) -> dict:
        return {
            "seq": record.seq,
            "timestamp": record.timestamp,
            "action_name": record.action_name,
            "reversibility_class": record.reversibility_class,
            "confidence": record.confidence,
            "threshold": record.threshold,
            "tier": record.tier,
            "autonomous": record.autonomous,
            "triggers": list(record.triggers),
            "rationale": record.rationale,
            "outcome": record.outcome,
        }
