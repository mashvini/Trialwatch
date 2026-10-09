"""Spec for T4 (verify_flags, banned_words_in) and the T6 guardrail (verify_challenge)."""
from __future__ import annotations

from helpers import implemented_or_skip

from fairtrace import verify
from fairtrace.schemas import Case, CaseRecord, Challenge, Flag, SourceLine

LINE = 'Defense counsel stood to cross-examine witness 1. Judge said the questions were "not necessary" and did not allow them.'


def _record() -> CaseRecord:
    return CaseRecord(
        case=Case(id="t", title="t", country="t"),
        source_lines=[SourceLine(id="H01-L012", doc="H01", text=LINE)],
    )


def _flag(**overrides) -> Flag:
    base = dict(
        id="F1",
        right_id="examine_witnesses",
        source_ids=["H01-L012"],
        quote="did not allow them",
        explanation="Potential issue with the right to examine witnesses.",
    )
    base.update(overrides)
    return Flag(**base)


def _verify(flags, settings, rights):
    return implemented_or_skip(verify.verify_flags, flags, _record(), settings, rights)


def test_valid_flag_passes(settings, rights):
    passed, rejected = _verify([_flag()], settings, rights)
    assert [f.id for f in passed] == ["F1"] and rejected == []


def test_unknown_source_is_rejected_with_a_reason(settings, rights):
    passed, rejected = _verify([_flag(source_ids=["H01-L999"])], settings, rights)
    assert passed == [] and rejected[0].verifier_notes


def test_flag_without_sources_is_rejected(settings, rights):
    passed, rejected = _verify([_flag(source_ids=[])], settings, rights)
    assert passed == [] and len(rejected) == 1


def test_quote_must_match_a_cited_line(settings, rights):
    passed, rejected = _verify([_flag(quote="the witness was threatened by police")], settings, rights)
    assert passed == [] and len(rejected) == 1


def test_quote_match_ignores_case_and_punctuation(settings, rights):
    passed, _ = _verify([_flag(quote="JUDGE SAID THE QUESTIONS WERE NOT NECESSARY")], settings, rights)
    assert len(passed) == 1


def test_unknown_right_is_rejected(settings, rights):
    passed, rejected = _verify([_flag(right_id="right_to_fly")], settings, rights)
    assert passed == [] and len(rejected) == 1


def test_banned_word_warns_but_keeps_the_flag(settings, rights):
    passed, rejected = _verify([_flag(explanation="This is a clear violation of the right.")], settings, rights)
    assert len(passed) == 1 and rejected == []
    assert passed[0].verifier_notes


def test_banned_words_in():
    assert implemented_or_skip(verify.banned_words_in, "A clear Violation, not guilty.", ["violation", "guilty"]) == [
        "violation",
        "guilty",
    ]
    assert implemented_or_skip(verify.banned_words_in, "Several violations", ["violation"]) == []


def test_challenge_without_a_valid_citation_is_downgraded():
    challenge = Challenge(flag_id="F1", state_argument="x", verdict="rebutted", source_ids=["H01-L099"])
    out = implemented_or_skip(verify.verify_challenge, challenge, _record())
    assert out.verdict == "not_addressed" and out.source_ids == []
    assert "downgraded" in out.reasoning.lower()
    assert challenge.verdict == "rebutted"  # the input is not mutated


def test_challenge_with_a_valid_citation_is_kept():
    challenge = Challenge(flag_id="F1", state_argument="x", verdict="supported", source_ids=["H01-L012", "H01-L099"])
    out = implemented_or_skip(verify.verify_challenge, challenge, _record())
    assert out.verdict == "supported" and out.source_ids == ["H01-L012"]
