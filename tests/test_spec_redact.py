"""Spec for T11 (redaction)."""
from __future__ import annotations

from helpers import implemented_or_skip

from fairtrace import redact


def test_redact_whole_words_longest_first_case_insensitive():
    mapping = {"Maria": "WITNESS-2", "Maria Santos": "DEFENDANT"}
    out = implemented_or_skip(redact.redact, "Maria Santos met maria. Mariana stayed.", mapping)
    assert out == "[DEFENDANT] met [WITNESS-2]. Mariana stayed."


def test_restore_round_trip():
    mapping = {"Maria Santos": "DEFENDANT"}
    redacted = implemented_or_skip(redact.redact, "Maria Santos spoke.", mapping)
    assert implemented_or_skip(redact.restore, redacted, mapping) == "Maria Santos spoke."
