"""Spec for T7 (Copy-Through Detector), using the synthetic demo documents.

Judgment paragraph 1 quotes the indictment (normal, outside the reasoning section: no flag).
Judgment paragraph 3 repeats the police report's conclusion inside the reasoning section: one flag.
"""
from __future__ import annotations

from helpers import implemented_or_skip

from fairtrace import verify
from fairtrace.analyzers.copy_through import CopyThrough, flags_from_report, normalize_words, shared_runs


def _report(settings, record):
    return implemented_or_skip(CopyThrough().run, record, settings, None)


def test_normalize_words():
    words = implemented_or_skip(normalize_words, "Having considered the evidence, the court finds")
    assert words == ["having", "considered", "the", "evidence", "the", "court", "finds"]


def test_shared_runs():
    source = "one two three four five six seven eight nine".split()
    judgment = "x one two three four five six seven eight y".split()
    assert implemented_or_skip(shared_runs, source, judgment, 8) == [(0, 1, 8)]
    assert implemented_or_skip(shared_runs, source, judgment, 9) == []


def test_copied_reasoning_is_found(settings, demo_record):
    report = _report(settings, demo_record)
    matches = [m for m in report.matches if m.judgment_id == "JDG-P003" and m.source_id == "POL-P002"]
    assert matches and matches[0].shared_words >= 25 and matches[0].in_reasoning


def test_quoted_charges_match_outside_the_reasoning(settings, demo_record):
    report = _report(settings, demo_record)
    assert any(m.judgment_id == "JDG-P001" and not m.in_reasoning for m in report.matches)


def test_unrelated_paragraphs_do_not_match(settings, demo_record):
    report = _report(settings, demo_record)
    assert not any(m.judgment_id in ("JDG-P002", "JDG-P004", "JDG-P005") for m in report.matches)


def test_coverage_figures(settings, demo_record):
    report = _report(settings, demo_record)
    assert 0 < report.coverage_overall < 1
    assert report.coverage_reasoning is not None and 0.3 < report.coverage_reasoning < 1


def test_flags_only_for_the_reasoning_section(settings, demo_record):
    flags = implemented_or_skip(flags_from_report, _report(settings, demo_record), settings)
    assert [f.id for f in flags] == ["F-CT-1"]
    assert set(flags[0].source_ids) == {"JDG-P003", "POL-P002"}
    assert flags[0].origin == "copy_through"
    assert flags[0].right_id == settings.copy_through["right_id"]


def test_copy_through_flags_pass_the_verifier(settings, rights, demo_record):
    flags = implemented_or_skip(flags_from_report, _report(settings, demo_record), settings)
    passed, rejected = implemented_or_skip(verify.verify_flags, flags, demo_record, settings, rights)
    assert len(passed) == 1 and rejected == []


def test_apply_stores_the_report_and_adds_flags(settings, demo_record):
    module = CopyThrough()
    report = _report(settings, demo_record)
    implemented_or_skip(module.apply, demo_record, report, settings)
    assert demo_record.copy_report == report
    assert [f.id for f in demo_record.flags if f.origin == "copy_through"] == ["F-CT-1"]
