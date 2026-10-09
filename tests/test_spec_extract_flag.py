"""Spec for T2 (extract) and T3 (flag), run against the mock fixtures."""
from __future__ import annotations

from helpers import implemented_or_skip

from fairtrace import extract, flag, verify
from fairtrace.llm import LLM


def _events(settings, record):
    return implemented_or_skip(extract.extract_events, record, LLM(settings, "mock"), settings)


def test_extract_events_cite_real_lines(settings, demo_record):
    events = _events(settings, demo_record)
    assert {e.hearing for e in events} == {"H01", "H02"}
    assert all(e.source_ids and set(e.source_ids) <= demo_record.line_ids() for e in events)
    assert len({e.id for e in events}) == len(events)


def test_flag_issues_in_mock_mode(settings, rights, demo_record):
    demo_record.events = _events(settings, demo_record)
    flags = implemented_or_skip(flag.flag_issues, demo_record, LLM(settings, "mock"), settings, rights)
    assert len(flags) == 6
    assert not any(sid.startswith("H02-") for f in flags for sid in f.source_ids)  # clean hearing
    assert all(f.status == "pending" and f.origin == "notes" for f in flags)
    assert len({f.id for f in flags}) == len(flags)


def test_the_verifier_catches_the_planted_mistake(settings, rights, demo_record):
    demo_record.events = _events(settings, demo_record)
    flags = implemented_or_skip(flag.flag_issues, demo_record, LLM(settings, "mock"), settings, rights)
    passed, rejected = implemented_or_skip(verify.verify_flags, flags, demo_record, settings, rights)
    assert [f.quote for f in rejected] == ["the investigator called the defendant a criminal"]
    assert len(passed) == 5
