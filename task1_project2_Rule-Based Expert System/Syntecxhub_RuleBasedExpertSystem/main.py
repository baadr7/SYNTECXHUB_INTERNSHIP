"""Command-line interface for the rule-based expert system.

Three usage modes:
    * Interactive  -> ``python main.py``  (pick symptoms by number or name)
    * Direct       -> ``python main.py --facts fever cough "sore throat"``
    * Inspection   -> ``python main.py --list``  (show symptoms and rules)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

from expert_system.display import (
    Palette,
    banner,
    render_error,
    render_report,
    render_symptoms,
)
from expert_system.engine import InferenceEngine
from expert_system.knowledge_loader import KnowledgeBase, KnowledgeBaseError

DEFAULT_KB_PATH = Path(__file__).resolve().parent / "knowledge_base.json"


def resolve_facts(
    raw_tokens: Sequence[str], known_symptoms: Sequence[str]
) -> Tuple[List[str], List[str]]:
    """Turn raw CLI/inline tokens into normalised facts.

    Accepts comma-separated values inside a token and bare tokens, as well as
    1-based numeric indices referring to the ``known_symptoms`` order.

    Returns:
        A ``(facts, unknown)`` tuple where *unknown* lists inputs that are
        neither a valid index nor a recognised symptom name.
    """
    segments: List[str] = []
    for token in raw_tokens:
        segments.extend(part.strip() for part in token.split(","))
    segments = [segment for segment in segments if segment]

    facts: List[str] = []
    unknown: List[str] = []
    lookup = {symptom.lower(): symptom for symptom in known_symptoms}

    for segment in segments:
        if segment.isdigit():
            index = int(segment)
            if 1 <= index <= len(known_symptoms):
                facts.append(known_symptoms[index - 1])
            else:
                unknown.append(segment)
        else:
            key = " ".join(segment.lower().split())
            if key in lookup:
                facts.append(lookup[key])
            else:
                unknown.append(segment)
    return facts, unknown


def interactive_select(symptoms: Sequence[str], palette: Palette) -> List[str]:
    """Prompt the user to select symptoms until a valid choice is given."""
    print(render_symptoms(symptoms, palette))
    while True:
        raw = input(
            "\nEnter symptom numbers or names (comma-separated), "
            "or press Enter to cancel: "
        ).strip()
        if not raw:
            return []
        facts, unknown = resolve_facts([raw], symptoms)
        if unknown:
            print(render_error(f"Unknown selection(s): {', '.join(unknown)}", palette))
            continue
        return facts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="expert-system",
        description="Rule-based expert system with forward chaining.",
    )
    parser.add_argument(
        "--facts",
        nargs="*",
        default=None,
        metavar="FACT",
        help="Facts to assert (names or 1-based indices). Comma or space separated.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List the available symptoms and all rules, then exit.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colour output.",
    )
    parser.add_argument(
        "--kb",
        default=str(DEFAULT_KB_PATH),
        help="Path to the knowledge base JSON file.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Program entry point. Returns a process exit code."""
    args = build_parser().parse_args(argv)
    palette = Palette(enabled=False if args.no_color else None)

    try:
        knowledge_base = KnowledgeBase.load(args.kb)
    except KnowledgeBaseError as exc:
        print(render_error(str(exc), palette))
        return 2

    print(banner(knowledge_base.title or "RULE-BASED EXPERT SYSTEM", palette))

    if args.list:
        print(render_symptoms(knowledge_base.symptoms, palette))
        print("\nRules:")
        for rule in knowledge_base.rules:
            antecedents = " AND ".join(rule.antecedents)
            print(f"  {rule.rule_id}: IF {antecedents} THEN {rule.consequent}")
        return 0

    if args.facts is not None:
        facts, unknown = resolve_facts(args.facts, knowledge_base.symptoms)
        if unknown:
            print(render_error(f"Unknown fact(s): {', '.join(unknown)}", palette))
            return 2
    else:
        facts = interactive_select(knowledge_base.symptoms, palette)

    if not facts:
        print(render_error("No symptom provided; nothing to infer.", palette))
        return 1

    print(f"\nSelected symptoms: {', '.join(facts)}\n")
    engine = InferenceEngine(knowledge_base)
    result = engine.infer(facts)
    print(render_report(result, palette))
    return 0


if __name__ == "__main__":
    sys.exit(main())