"""Forward-chaining inference engine with a transparent audit trail.

The engine repeatedly applies all rules whose antecedents are satisfied in the
working memory (:class:`FactBase`). Facts derived by a rule are added and may,
in turn, trigger further rules: this is multi-step (chained) forward inference.
Every activation is recorded so the reasoning path can be inspected afterwards.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Sequence, Set, Tuple

from .fact_base import FactBase
from .knowledge_loader import KnowledgeBase
from .rule import Rule


@dataclass(frozen=True)
class InferenceStep:
    """A single, immutable rule activation recorded during inference.

    Attributes:
        iteration: The inference cycle (1-based) in which the rule fired.
        rule_id: Identifier of the fired rule.
        antecedents: Facts that satisfied the rule.
        consequent: The fact produced by the rule.
        description: Human-readable intent of the rule.
    """

    iteration: int
    rule_id: str
    antecedents: Tuple[str, ...]
    consequent: str
    description: str


@dataclass
class InferenceResult:
    """The outcome of a complete inference run.

    Attributes:
        initial_facts: Facts present before inference started.
        derived_facts: New facts produced by the engine (in order).
        final_facts: The complete working memory after inference.
        steps: Ordered trail of rule activations.
        reached: Whether at least one rule fired.
    """

    initial_facts: Tuple[str, ...]
    derived_facts: List[str] = field(default_factory=list)
    final_facts: Tuple[str, ...] = ()
    steps: List[InferenceStep] = field(default_factory=list)
    reached: bool = False

    @property
    def fired_rule_ids(self) -> List[str]:
        """Return the ids of the rules that fired, in activation order."""
        return [step.rule_id for step in self.steps]


class InferenceEngine:
    """A deterministic forward-chaining engine.

    The engine is a pure function of ``(knowledge_base, facts)``: running it
    twice on the same inputs always yields the same result, which makes it
    reproducible and unit-testable.
    """

    __slots__ = ("_kb", "_max_iterations")

    def __init__(self, knowledge_base: KnowledgeBase, max_iterations: int = 1000) -> None:
        if max_iterations <= 0:
            raise ValueError("max_iterations must be a positive integer.")
        self._kb = knowledge_base
        self._max_iterations = max_iterations

    def infer(self, initial_facts: Sequence[str]) -> InferenceResult:
        """Run forward chaining starting from *initial_facts*.

        Args:
            initial_facts: Facts asserted by the user (e.g. observed symptoms).

        Returns:
            An :class:`InferenceResult` describing the derived facts and the
            ordered trail of rule activations.

        Raises:
            TypeError: If *initial_facts* is not an iterable of strings.
        """
        if isinstance(initial_facts, (str, bytes)):
            raise TypeError("initial_facts must be a sequence of facts, not a string.")

        fact_base = FactBase()
        for fact in initial_facts:
            fact_base.add(fact)
        initial_snapshot = fact_base.snapshot()

        steps: List[InferenceStep] = []
        derived: List[str] = []
        fired_rule_ids: Set[str] = set()

        iteration = 0
        changed = True
        while changed and iteration < self._max_iterations:
            changed = False
            iteration += 1
            for rule in self._kb.rules:
                if rule.rule_id in fired_rule_ids:
                    continue
                if not rule.is_triggered(fact_base.snapshot()):
                    continue
                is_new = fact_base.add(rule.consequent)
                steps.append(
                    InferenceStep(
                        iteration=iteration,
                        rule_id=rule.rule_id,
                        antecedents=tuple(rule.antecedents),
                        consequent=rule.consequent,
                        description=rule.description,
                    )
                )
                fired_rule_ids.add(rule.rule_id)
                if is_new:
                    derived.append(rule.consequent)
                changed = True

        return InferenceResult(
            initial_facts=tuple(sorted(initial_snapshot)),
            derived_facts=derived,
            final_facts=tuple(sorted(fact_base.snapshot())),
            steps=steps,
            reached=bool(steps),
        )

    def __repr__(self) -> str:
        return (
            f"InferenceEngine(rules={len(self._kb)}, "
            f"max_iterations={self._max_iterations})"
        )