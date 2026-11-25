"""Loading and validation of the knowledge base (rules + metadata).

The knowledge base is stored as JSON so that domain experts can maintain the
rules without touching the source code. This module validates the structure
thoroughly and fails fast with precise, actionable error messages.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence

from .rule import Rule


class KnowledgeBaseError(Exception):
    """Raised when the knowledge base file is missing or malformed."""


class KnowledgeBase:
    """An immutable, validated collection of rules and their metadata.

    Attributes:
        rules: The validated rules, in declaration order.
        symptoms: Known observable facts a user may report.
        diagnoses: Every conclusion the engine may derive, i.e. the full set
            of facts that can appear as a rule consequent (intermediate
            findings as well as final diagnoses).
        title: Human-readable title of the knowledge base.
    """

    __slots__ = ("rules", "symptoms", "diagnoses", "title", "_by_id")

    def __init__(
        self,
        rules: Sequence[Rule],
        symptoms: Sequence[str] | None = None,
        diagnoses: Sequence[str] | None = None,
        title: str = "",
    ) -> None:
        if not rules:
            raise KnowledgeBaseError("The knowledge base must contain at least one rule.")

        seen: Dict[str, Rule] = {}
        for rule in rules:
            if rule.rule_id in seen:
                raise KnowledgeBaseError(f"Duplicate rule id detected: '{rule.rule_id}'.")
            seen[rule.rule_id] = rule

        self.rules: List[Rule] = list(rules)
        self.symptoms: List[str] = list(symptoms or [])
        self.diagnoses: List[str] = list(diagnoses or [])
        self.title: str = title
        self._by_id: Dict[str, Rule] = seen

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "KnowledgeBase":
        """Validate and build a knowledge base from a parsed JSON mapping."""
        if not isinstance(data, Mapping):
            raise KnowledgeBaseError("Knowledge base root must be a JSON object.")

        raw_rules = data.get("rules")
        if not isinstance(raw_rules, list) or not raw_rules:
            raise KnowledgeBaseError("'rules' must be a non-empty JSON array.")

        rules: List[Rule] = []
        for index, raw_rule in enumerate(raw_rules):
            if not isinstance(raw_rule, Mapping):
                raise KnowledgeBaseError(f"Rule at index {index} must be a JSON object.")
            for required in ("id", "if", "then"):
                if required not in raw_rule:
                    raise KnowledgeBaseError(
                        f"Rule at index {index} is missing the '{required}' field."
                    )
            if not isinstance(raw_rule["if"], list) or not raw_rule["if"]:
                raise KnowledgeBaseError(
                    f"Rule '{raw_rule.get('id', index)}': 'if' must be a non-empty array."
                )
            try:
                rules.append(Rule.from_dict(raw_rule))
            except (ValueError, TypeError) as exc:
                raise KnowledgeBaseError(
                    f"Invalid rule at index {index}: {exc}"
                ) from exc

        def _as_str_list(key: str) -> List[str]:
            value = data.get(key, [])
            if not isinstance(value, list):
                raise KnowledgeBaseError(f"'{key}' must be a JSON array when present.")
            return [str(item) for item in value]

        return cls(
            rules=rules,
            symptoms=_as_str_list("symptoms"),
            diagnoses=_as_str_list("diagnoses"),
            title=str(data.get("title", "")),
        )

    @classmethod
    def load(cls, path: str | Path) -> "KnowledgeBase":
        """Load a knowledge base from a ``.json`` file on disk.

        Raises:
            KnowledgeBaseError: If the file is missing, unreadable, or invalid.
        """
        file_path = Path(path)
        if not file_path.is_file():
            raise KnowledgeBaseError(f"Knowledge base file not found: {file_path}")
        try:
            raw_text = file_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise KnowledgeBaseError(f"Cannot read '{file_path}': {exc}") from exc
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise KnowledgeBaseError(
                f"Invalid JSON in '{file_path}' at line {exc.lineno}, "
                f"column {exc.colno}: {exc.msg}"
            ) from exc
        return cls.from_dict(parsed)

    def get_rule(self, rule_id: str) -> Rule:
        """Return the rule with the given id, or raise :class:`KeyError`."""
        return self._by_id[rule_id]

    def __len__(self) -> int:
        return len(self.rules)

    def __iter__(self):
        return iter(self.rules)

    def __repr__(self) -> str:
        return (
            f"KnowledgeBase(title={self.title!r}, rules={len(self.rules)}, "
            f"symptoms={len(self.symptoms)}, diagnoses={len(self.diagnoses)})"
        )
