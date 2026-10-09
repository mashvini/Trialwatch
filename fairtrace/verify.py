"""Check every model output against the record. Plain code, no model.

This module is the main answer to "how do you stop the AI from inventing things?".
"""
from __future__ import annotations

from .config import Settings
from .schemas import CaseRecord, Challenge, Flag
from .taxonomy import Right


def banned_words_in(text: str, banned: list[str]) -> list[str]:
    """T4. Return the banned words found in `text` (whole words, case-insensitive), in list order.

    Example: banned_words_in("A clear violation.", ["violation", "guilty"]) -> ["violation"]
    "Violations" does not match "violation" unless it is in the list itself (config lists both).
    """
    raise NotImplementedError("T4: banned word check (see the docstring in verify.py)")


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
    raise NotImplementedError("T4: verify flags (see the docstring in verify.py)")


def verify_challenge(challenge: Challenge, record: CaseRecord) -> Challenge:
    """T6 guardrail. Clean one Devil's Advocate result.

    - Drop source_ids that don't exist in record.line_ids().
    - If the verdict is "rebutted" or "supported" but no valid source_ids remain, set the verdict
      to "not_addressed" and append " (Verdict downgraded: no valid citation.)" to reasoning.
    - Return a new Challenge; don't mutate the input.

    Spec: tests/test_spec_verify.py
    """
    raise NotImplementedError("T6: verify challenge (see the docstring in verify.py)")
