"""A single if-then production rule used by the forward-chaining engine."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Sequence, Tuple

from .fact_base import FactBase


class Rule:
    """An ``IF <antecedents...> THEN <consequent>`` production rule.

    Attributes:
        rule_id: Unique identifier used for logging and traceability.
        antecedents: Ordered tuple of normalised facts that must all be known
            for the rule to fire (logical AND).
        consequent: The single normalised fact derived when the rule fires.
        description: Human-readable explanation of the rule's intent.
    """

    __slots__ = ("rule_id", "antecedents", "consequent", "description")

    def __init__(
        self,
        rule_id: str,
        antecedents: Iterable[str],
        consequent: str,
        description: str = "",
    ) -> None:
        norm_id = str(rule_id).strip()
        if not norm_id:
            raise ValueError("rule_id cannot be empty.")

        norm_antecedents: Tuple[str, ...] = tuple(
            FactBase.normalise(a) for a in antecedents
        )
        if not norm_antecedents:
            raise ValueError(f"Rule '{norm_id}' must have at least one antecedent.")

        self.rule_id: str = norm_id
        self.antecedents: Tuple[str, ...] = norm_antecedents
        self.consequent: str = FactBase.normalise(consequent)
        self.description: str = description.strip()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Rule":
        """Build a :class:`Rule` from a mapping (e.g. a JSON object)."""
        return cls(
            rule_id=data["id"],
            antecedents=data["if"],
            consequent=data["then"],
            description=data.get("description", ""),
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the rule back to a JSON-compatible mapping."""
        return {
            "id": self.rule_id,
            "if": list(self.antecedents),
            "then": self.consequent,
            "description": self.description,
        }

    def is_triggered(self, known_facts: Iterable[str]) -> bool:
        """Return ``True`` if every antecedent is present in *known_facts*."""
        facts = {FactBase.normalise(f) for f in known_facts}
        return all(antecedent in facts for antecedent in self.antecedents)

    def missing_antecedents(self, known_facts: Iterable[str]) -> Sequence[str]:
        """Return the antecedents that are *not* satisfied (diagnostic helper)."""
        facts = {FactBase.normalise(f) for f in known_facts}
        return [a for a in self.antecedents if a not in facts]

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Rule) and other.rule_id == self.rule_id

    def __hash__(self) -> int:
        return hash(self.rule_id)

    def __repr__(self) -> str:
        antecedent_str = " AND ".join(self.antecedents)
        return f"Rule({self.rule_id}: IF {antecedent_str} THEN {self.consequent})"