"""Check every model output against the record. Plain code, no model.

This module is the main answer to "how do you stop the AI from inventing things?".
"""
from __future__ import annotations

import re

from rapidfuzz import fuzz, utils

from .config import Settings
from .schemas import CaseRecord, Challenge, Flag
from .taxonomy import Right


def banned_words_in(text: str, banned: list[str]) -> list[str]:
    """T4. Return the banned words found in `text` (whole words, case-insensitive), in list order.

    Example: banned_words_in("A clear violation.", ["violation", "guilty"]) -> ["violation"]
    "Violations" does not match "violation" unless it is in the list itself (config lists both).
    """
    return [word for word in banned if re.search(rf"\b{re.escape(word)}\b", text, re.IGNORECASE)]


def verify_flags(
    flags: list[Flag], record: CaseRecord, settings: Settings, rights: list[Right]
) -> tuple[list[Flag], list[Flag]]:
    """T4. Split flags into (passed, rejected). Never drop a flag silently.

    Hard failures -> rejected, with the reason appended to flag.verifier_notes:
    - right_id is not in `rights`
    - source_ids is empty, or contains an id not in record.line_ids()
    - quote does not match any cited line:
        rapidfuzz.fuzz.partial_ratio(quote, line.text, processor=rapidfuzz.utils.default_process)
        < settings.verify["quote_match_threshold"] for every cited line

    Soft warning -> passed, with a note in verifier_notes:
    - the explanation contains a word from settings.verify["banned_words"] (use banned_words_in)

    Spec: tests/test_spec_verify.py
    """
    right_ids = {r.id for r in rights}
    lines = record.lines_by_id()
    threshold = settings.verify["quote_match_threshold"]
    banned = settings.verify.get("banned_words", [])
    passed: list[Flag] = []
    rejected: list[Flag] = []
    for flag in flags:
        failures = _hard_failures(flag, right_ids, lines, threshold)
        notes = list(flag.verifier_notes) + failures
        found = banned_words_in(flag.explanation, banned)
        if found:
            notes.append(f"Wording: the explanation uses conclusory words ({', '.join(found)}). Rephrase as a potential issue.")
        checked = flag.model_copy(update={"verifier_notes": notes})
        (rejected if failures else passed).append(checked)
    return passed, rejected


def _hard_failures(flag: Flag, right_ids: set[str], lines: dict, threshold: float) -> list[str]:
    """Reasons this flag must be rejected; empty if it passes."""
    failures: list[str] = []
    if flag.right_id not in right_ids:
        failures.append(f"Rejected: right '{flag.right_id}' is not in the rights list.")
    if not flag.source_ids:
        failures.append("Rejected: the flag cites no source lines.")
        return failures
    unknown = [sid for sid in flag.source_ids if sid not in lines]
    if unknown:
        failures.append(f"Rejected: cited lines do not exist: {', '.join(unknown)}.")
    cited = [lines[sid].text for sid in flag.source_ids if sid in lines]
    if cited and not any(
        fuzz.partial_ratio(flag.quote, text, processor=utils.default_process) >= threshold for text in cited
    ):
        failures.append(f'Rejected: the quote "{flag.quote}" does not match any cited line.')
    return failures


def verify_challenge(challenge: Challenge, record: CaseRecord) -> Challenge:
    """T6 guardrail. Clean one Devil's Advocate result.

    - Drop source_ids that don't exist in record.line_ids().
    - If the verdict is "rebutted" or "supported" but no valid source_ids remain, set the verdict
      to "not_addressed" and append " (Verdict downgraded: no valid citation.)" to reasoning.
    - Return a new Challenge; don't mutate the input.

    Spec: tests/test_spec_verify.py
    """
    known = record.line_ids()
    valid = [sid for sid in challenge.source_ids if sid in known]
    update: dict = {"source_ids": valid}
    if challenge.verdict in ("rebutted", "supported") and not valid:
        update["verdict"] = "not_addressed"
        update["reasoning"] = challenge.reasoning + " (Verdict downgraded: no valid citation.)"
    return challenge.model_copy(update=update)
