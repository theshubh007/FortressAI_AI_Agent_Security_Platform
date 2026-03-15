"""Reversibility policy loader and action classifier (Table I as code).

Loads ``policy/reversibility_taxonomy.yaml`` and exposes the per-class tier
ceiling, confidence threshold, and autonomy mode, plus a name-based
classifier. This is the single source of truth for the blast-radius envelope.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .types import ReversibilityClass, Tier

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "tiered-autonomy requires PyYAML to load the reversibility policy. "
        "Install it with `pip install pyyaml`."
    ) from exc

DEFAULT_POLICY_PATH = (
    Path(__file__).resolve().parent.parent / "policy" / "reversibility_taxonomy.yaml"
)


@dataclass(frozen=True)
class ClassSpec:
    rclass: ReversibilityClass
    representative_actions: List[str]
    impact_scope: str
    recommended_tier: Tier
    threshold: Optional[float]
    autonomy: str  # "always" | "gated" | "never"

    @property
    def never_autonomous(self) -> bool:
        return self.autonomy == "never"

    @property
    def always_autonomous(self) -> bool:
        return self.autonomy == "always"


class ReversibilityPolicy:
    """The blast-radius envelope: reversibility class -> tier + threshold."""

    def __init__(self, specs: Dict[ReversibilityClass, ClassSpec],
                 rules: List[Tuple[re.Pattern, ReversibilityClass]]):
        self._specs = specs
        self._rules = rules

    # ---- construction -----------------------------------------------------
    @classmethod
    def load(cls, path: Path | str = DEFAULT_POLICY_PATH) -> "ReversibilityPolicy":
        data = yaml.safe_load(Path(path).read_text())
        specs: Dict[ReversibilityClass, ClassSpec] = {}
        for name, body in data["classes"].items():
            rclass = ReversibilityClass[name]
            specs[rclass] = ClassSpec(
                rclass=rclass,
                representative_actions=list(body.get("representative_actions", [])),
                impact_scope=str(body.get("impact_scope", "")),
                recommended_tier=Tier[body["recommended_tier"]],
                threshold=body.get("threshold"),
                autonomy=str(body.get("autonomy", "gated")),
            )
        rules: List[Tuple[re.Pattern, ReversibilityClass]] = []
        for rule in data.get("classification_rules", []):
            rules.append((re.compile(rule["pattern"], re.IGNORECASE),
                          ReversibilityClass[rule["class"]]))
        return cls(specs, rules)

    # ---- lookups ----------------------------------------------------------
    def spec(self, rclass: ReversibilityClass) -> ClassSpec:
        return self._specs[rclass]

    def threshold(self, rclass: ReversibilityClass) -> Optional[float]:
        return self._specs[rclass].threshold

    def tier_ceiling(self, rclass: ReversibilityClass) -> Tier:
        """Highest tier the agent may occupy for this class when confident."""
        return self._specs[rclass].recommended_tier

    def is_never_autonomous(self, rclass: ReversibilityClass) -> bool:
        return self._specs[rclass].never_autonomous

    def is_always_autonomous(self, rclass: ReversibilityClass) -> bool:
        return self._specs[rclass].always_autonomous

    # ---- classification ---------------------------------------------------
    def classify(self, action) -> Optional[ReversibilityClass]:
        """Return the action's reversibility class.

        Explicit ``action.reversibility`` wins. Otherwise match the action name
        against the declarative rules (first match wins). Unmatched -> None,
        which the controller treats as an UNCLASSIFIED_ACTION escalation.
        """
        if getattr(action, "reversibility", None) is not None:
            return action.reversibility
        name = getattr(action, "name", str(action))
        for pattern, rclass in self._rules:
            if pattern.search(name):
                return rclass
        return None

    @property
    def classes(self) -> Dict[ReversibilityClass, ClassSpec]:
        return dict(self._specs)
