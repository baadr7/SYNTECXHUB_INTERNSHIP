"""Human-readable explanations of the inference trail (the reasoning path).

Given an :class:`~expert_system.engine.InferenceResult`, this module rebuilds
*why* each fact is true, recursively, so a user can follow multi-step chains
from the original symptoms down to the final conclusions.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set

from .engine import InferenceResult, InferenceStep

_SEPARATOR = "=" * 62


class Explanator:
    """Turns a raw inference trail into a justified, tree-like narrative."""

    __slots__ = ("_result", "_provenance")

    def __init__(self, result: InferenceResult) -> None:
        self._result = result
        self._provenance: Dict[str, InferenceStep] = {}
        for step in result.steps:
            self._provenance.setdefault(step.consequent, step)

    def explain_fact(self, fact: str, _seen: Optional[Set[str]] = None) -> str:
        """Return an indented justification tree for *fact*.

        Base facts (provided by the user) terminate the recursion with the tag
        ``[given]``. Derived facts are expanded through their proving rule.
        """
        seen = _seen if _seen is not None else set()
        step = self._provenance.get(fact)
        if step is None or fact in seen:
            return f"{fact}  [given]"
        seen = seen | {fact}
        children = "\n".join(
            self._indent(self.explain_fact(antecedent, seen))
            for antecedent in step.antecedents
        )
        return f"{fact}  [from {step.rule_id}]\n  └─ because:\n{children}"

    @staticmethod
    def _indent(text: str, spaces: int = 6) -> str:
        pad = " " * spaces
        return "\n".join(pad + line for line in text.splitlines())

    def narrative(self) -> str:
        """Return the full step-by-step reasoning path as readable text."""
        lines: List[str] = [_SEPARATOR, "REASONING PATH", _SEPARATOR]
        if not self._result.steps:
            lines.append("No rule fired: no conclusion could be derived.")
            return "\n".join(lines)
        for step in self._result.steps:
            antecedent_str = " AND ".join(step.antecedents)
            lines.append(
                f"[Step {step.iteration}] {step.rule_id}: "
                f"IF {antecedent_str} THEN {step.consequent}"
            )
            if step.description:
                lines.append(f"          · {step.description}")
        return "\n".join(lines)

    def explanation_report(self) -> str:
        """Return a per-conclusion explanation report with justification trees."""
        lines: List[str] = [_SEPARATOR, "WHY THESE CONCLUSIONS?", _SEPARATOR]
        if not self._result.derived_facts:
            lines.append("No new fact was derived from the provided symptoms.")
            return "\n".join(lines)
        for fact in self._result.derived_facts:
            lines.append(self.explain_fact(fact))
            lines.append("")
        return "\n".join(lines).rstrip()

    def __repr__(self) -> str:
        return f"Explanator(steps={len(self._result.steps)})"
