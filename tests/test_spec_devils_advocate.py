"""Spec for T6 (Devil's Advocate), run against the mock fixture."""
from __future__ import annotations

from helpers import implemented_or_skip

from fairtrace.analyzers.devils_advocate import DevilsAdvocate
from fairtrace.llm import LLM


def _run(settings, record):
    return implemented_or_skip(DevilsAdvocate().run, record, settings, LLM(settings, "mock"))


def test_one_challenge_per_flag(settings, demo_record, fixture_flags):
    demo_record.flags = fixture_flags
    result = _run(settings, demo_record)
    # the fixture also holds a challenge for F-CT-1, which isn't in this record: it must be ignored
    assert sorted(c.flag_id for c in result.challenges) == sorted(f.id for f in fixture_flags)


def test_rejected_flags_are_not_challenged(settings, demo_record, fixture_flags):
    fixture_flags[0].status = "rejected"
    demo_record.flags = fixture_flags
    result = _run(settings, demo_record)
    assert fixture_flags[0].id not in {c.flag_id for c in result.challenges}


def test_bad_citation_is_downgraded(settings, demo_record, fixture_flags):
    demo_record.flags = fixture_flags
    by_flag = {c.flag_id: c for c in _run(settings, demo_record).challenges}
    assert by_flag["F-H01-4"].verdict == "not_addressed"
    assert by_flag["F-H01-4"].source_ids == []


def test_every_verdict_rests_on_real_lines(settings, demo_record, fixture_flags):
    demo_record.flags = fixture_flags
    for challenge in _run(settings, demo_record).challenges:
        assert set(challenge.source_ids) <= demo_record.line_ids()
        if challenge.verdict in ("rebutted", "supported"):
            assert challenge.source_ids
