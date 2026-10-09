"""Spec for T9 (export)."""
from __future__ import annotations

from helpers import implemented_or_skip

from fairtrace import export
from fairtrace.schemas import Challenge, Flag


def _flags():
    accepted = Flag(
        id="F1",
        right_id="examine_witnesses",
        source_ids=["H01-L012"],
        quote="did not allow them",
        explanation="ACCEPTED-EXPLANATION",
        status="accepted",
        missing_facts=["What did the defense intend to ask?"],
    )
    pending = Flag(
        id="F2",
        right_id="public_hearing",
        source_ids=["H01-L006"],
        quote="turned away three journalists",
        explanation="PENDING-EXPLANATION",
    )
    return [accepted, pending]


def test_export_contains_accepted_issues_only(rights, demo_record):
    demo_record.flags = _flags()
    md = implemented_or_skip(export.export_markdown, demo_record, rights, "Test Reviewer")
    assert md.startswith("# Draft findings:")
    assert "ACCEPTED-EXPLANATION" in md and "PENDING-EXPLANATION" not in md
    assert "Right to examine witnesses" in md and "Right to a public hearing" not in md
    assert "H01-L012" in md and "Test Reviewer" in md
    assert "SYNTHETIC" in md.upper()
    assert "What did the defense intend to ask?" in md


def test_export_includes_the_devils_advocate(rights, demo_record):
    demo_record.flags = _flags()
    demo_record.challenges = [
        Challenge(flag_id="F1", state_argument="STATE-ARGUMENT", verdict="not_addressed", reasoning="r")
    ]
    md = implemented_or_skip(export.export_markdown, demo_record, rights, "Test Reviewer")
    assert "STATE-ARGUMENT" in md
