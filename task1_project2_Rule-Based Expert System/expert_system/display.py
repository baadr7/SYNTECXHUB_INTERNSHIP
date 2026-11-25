"""Presentation layer: formatted console output for the expert system.

Keeps rendering concerns (banners, tables, colours) separate from the
inference logic. Colour output degrades gracefully to plain text on terminals
that do not support ANSI escape codes.
"""

from __future__ import annotations

import os
import sys
from typing import Sequence

from .engine import InferenceResult
from .explanation import Explanator

_WIDTH = 62


class Palette:
    """ANSI colour helpers that respect the NO_COLOR convention."""

    def __init__(self, enabled: bool | None = None) -> None:
        if enabled is None:
            enabled = bool(sys.stdout.isatty()) and os.environ.get("NO_COLOR") is None
        self.enabled = enabled

    def _wrap(self, code: str, text: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.enabled else text

    def bold(self, text: str) -> str:
        return self._wrap("1", text)

    def green(self, text: str) -> str:
        return self._wrap("32", text)

    def yellow(self, text: str) -> str:
        return self._wrap("33", text)

    def cyan(self, text: str) -> str:
        return self._wrap("36", text)

    def red(self, text: str) -> str:
        return self._wrap("31", text)


def banner(title: str, palette: Palette) -> str:
    """Return a centred banner for *title*."""
    return "\n".join(
        ["=" * _WIDTH, palette.bold(title.center(_WIDTH)), "=" * _WIDTH]
    )


def render_symptoms(symptoms: Sequence[str], palette: Palette) -> str:
    """Return a numbered list of selectable symptoms."""
    lines = [palette.cyan("Available symptoms:")]
    for index, symptom in enumerate(symptoms, start=1):
        lines.append(f"  {index:>2}. {symptom}")
    return "\n".join(lines)


def render_trace(result: InferenceResult, palette: Palette) -> str:
    """Return the step-by-step inference trace as a formatted table."""
    if not result.steps:
        return palette.yellow("No rule fired during inference.")
    lines = [palette.cyan("Inference trace:")]
    for step in result.steps:
        antecedents = " AND ".join(step.antecedents)
        lines.append(
            f"  [{step.iteration}] {palette.bold(step.rule_id)}: "
            f"{antecedents} -> {palette.green(step.consequent)}"
        )
    return "\n".join(lines)


def render_conclusions(result: InferenceResult, palette: Palette) -> str:
    """Return the list of derived conclusions (or an informative message)."""
    if not result.derived_facts:
        return palette.yellow("No conclusion could be derived from the given facts.")
    lines = [palette.cyan("Conclusions:")]
    for fact in result.derived_facts:
        lines.append(f"  * {palette.green(fact)}")
    return "\n".join(lines)


def render_report(result: InferenceResult, palette: Palette) -> str:
    """Return the complete end-of-run report: trace, conclusions, reasoning."""
    explanator = Explanator(result)
    parts = [
        render_trace(result, palette),
        "",
        render_conclusions(result, palette),
        "",
        explanator.narrative(),
        "",
        explanator.explanation_report(),
    ]
    return "\n".join(parts)


def render_error(message: str, palette: Palette) -> str:
    """Return a formatted error message."""
    return palette.red(f"Error: {message}")
