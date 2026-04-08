"""Mutation helpers for deterministic scoring."""

from __future__ import annotations

import re


def _replace_once(source: str, pattern: str, replacement: str, *, use_regex: bool = False) -> str | None:
    if use_regex:
        mutated, count = re.subn(pattern, replacement, source, count=1)
        return mutated if count else None

    if pattern not in source:
        return None

    mutated = source.replace(pattern, replacement, 1)
    return mutated if mutated != source else None


def generate_mutations(code: str) -> list[str]:
    candidates = []
    mutation_specs = [
        ("==", "!=", False),
        ("!=", "==", False),
        ("<=", "<", False),
        ("<", "<=", False),
        (">=", ">", False),
        (">", ">=", False),
        ("+", "-", False),
        ("-", "+", False),
        ("*", "/", False),
        ("/", "*", False),
        ("%", "*", False),
        (r"\band\b", "or", True),
        (r"\bor\b", "and", True),
        (r"\bTrue\b", "False", True),
        (r"\bFalse\b", "True", True),
        (r"\bNone\b", "0", True),
        (r"\breturn\b", "return None #", True),
    ]

    for pattern, replacement, use_regex in mutation_specs:
        mutated = _replace_once(code, pattern, replacement, use_regex=use_regex)
        if mutated and mutated not in candidates and mutated != code:
            candidates.append(mutated)

    return candidates

