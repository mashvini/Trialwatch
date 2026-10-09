"""T8: questions for the monitor (Gap Finder) and the downloadable checklist."""
from __future__ import annotations

from fairtrace import export
from fairtrace.schemas import Challenge


def test_questions_are_grouped_by_hearing_and_skip_rejected_flags(demo_record, fixture_flags):
    fixture_flags[0].status = "rejected"
    demo_record.flags = fixture_flags
    groups = export.monitor_questions(demo_record, ("pending", "accepted", "needs_facts"))
    assert list(groups) == ["Hearing H01 (2026-03-02)"]
    flag_ids = {item.flag_id for item in groups["Hearing H01 (2026-03-02)"]}
    assert fixture_flags[0].id not in flag_ids and fixture_flags[1].id in flag_ids


def test_silent_record_becomes_a_question_only_when_asked(demo_record, fixture_flags):
    demo_record.flags = fixture_flags
    demo_record.challenges = [
        Challenge(flag_id=fixture_flags[0].id, state_argument="STATE-ARGUMENT", verdict="not_addressed"),
        Challenge(flag_id=fixture_flags[1].id, state_argument="REBUTTED-ARGUMENT", verdict="rebutted", source_ids=["H01-L009"]),
    ]
    statuses = ("pending",)
    with_challenges = export.monitor_questions(demo_record, statuses, include_challenges=True)
    questions = [item.question for items in with_challenges.values() for item in items]
    assert any("STATE-ARGUMENT" in q for q in questions)
    assert not any("REBUTTED-ARGUMENT" in q for q in questions)
    without = export.monitor_questions(demo_record, statuses)
    assert not any(item.source == "devils_advocate" for items in without.values() for item in items)


def test_checklist_is_markdown_with_tick_boxes(demo_record, fixture_flags):
    demo_record.flags = fixture_flags
    groups = export.monitor_questions(demo_record, ("pending",))
    md = export.questions_checklist(demo_record, groups)
    assert md.startswith("# Questions for the monitor:")
    assert "SYNTHETIC" in md and "## Hearing H01" in md and "- [ ] " in md
