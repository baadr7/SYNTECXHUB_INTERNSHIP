"""Working memory for the rule-based expert system.

The :class:`FactBase` stores the set of facts currently known to be true.
Facts are normalised (trimmed and lower-cased) so that matching between the
user input and the rule antecedents is case-insensitive and whitespace-safe.
"""

from __future__ import annotations

from typing import Iterable, Iterator, FrozenSet, Set


class FactBase:
    """A mutable set of known facts with normalisation and deduplication."""

    __slots__ = ("_facts",)

    def __init__(self, facts: Iterable[str] | None = None) -> None:
        self._facts: Set[str] = set()
        if facts is not None:
            self.add_many(facts)

    @staticmethod
    def normalise(fact: str) -> str:
        """Return the canonical token for *fact*.

        Raises:
            TypeError: If *fact* is not a string.
            ValueError: If *fact* is empty once normalised.
        """
        if not isinstance(fact, str):
            raise TypeError(f"Fact must be a string, got {type(fact).__name__}.")
        token = " ".join(fact.strip().lower().split())
        if not token:
            raise ValueError("A fact cannot be empty.")
        return token

    def add(self, fact: str) -> bool:
        """Add *fact* to the base.

        Returns:
            ``True`` if the fact was newly inserted, ``False`` if it was
            already present.
        """
        token = self.normalise(fact)
        if token in self._facts:
            return False
        self._facts.add(token)
        return True

    def add_many(self, facts: Iterable[str]) -> int:
        """Add several facts and return how many were new."""
        return sum(1 for fact in facts if self.add(fact))

    def contains(self, fact: str) -> bool:
        """Return ``True`` if *fact* (normalised) is known."""
        return self.normalise(fact) in self._facts

    def snapshot(self) -> FrozenSet[str]:
        """Return an immutable view of the current facts."""
        return frozenset(self._facts)

    def __iter__(self) -> Iterator[str]:
        return iter(sorted(self._facts))

    def __len__(self) -> int:
        return len(self._facts)

    def __contains__(self, fact: object) -> bool:
        return isinstance(fact, str) and self.normalise(fact) in self._facts

    def __repr__(self) -> str:
        return f"FactBase({sorted(self._facts)!r})"
