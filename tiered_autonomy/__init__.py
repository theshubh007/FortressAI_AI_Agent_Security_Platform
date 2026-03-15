"""Tiered Autonomy -- reference implementation for the IEEE SMC 2026 paper.

Public API is assembled at integration time; import submodules directly during
development (e.g. ``from tiered_autonomy.taxonomy import ReversibilityPolicy``).
"""
from .types import (
    Action,
    AuditRecord,
    Decision,
    EscalationTrigger,
    ReversibilityClass,
    Tier,
)

__all__ = [
    "Action",
    "AuditRecord",
    "Decision",
    "EscalationTrigger",
    "ReversibilityClass",
    "Tier",
]

__version__ = "0.1.0"
