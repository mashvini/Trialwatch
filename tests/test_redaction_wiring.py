"""T11 wiring: lines are redacted after ingest (IDs unchanged) and names come back only on export, if asked."""
from __future__ import annotations

from fairtrace import export, redact
from fairtrace.schemas import Flag, SourceLine

NAMES = {"Maria Santos": "DEFENDANT"}


def test_redact_lines_keeps_ids_and_replaces_names():
    lines = [SourceLine(id="H01-L005", doc="H01", text="Maria Santos was brought in.")]
    out = redact.redact_lines(lines, NAMES)
    assert [(line.id, line.text) for line in out] == [("H01-L005", "[DEFENDANT] was brought in.")]
    assert lines[0].text == "Maria Santos was brought in."  # the input is not mutated


def test_no_names_file_means_no_change():
    lines = [SourceLine(id="H01-L005", doc="H01", text="Maria Santos was brought in.")]
    assert redact.redact_lines(lines, {}) == lines


def test_export_restores_names_only_when_asked(rights, demo_record):
    demo_record.source_lines = redact.redact_lines(
        [SourceLine(id="H01-L012", doc="H01", text="Maria Santos was not allowed to question the witness.")], NAMES
    )
    demo_record.flags = [
        Flag(
            id="F1",
            right_id="examine_witnesses",
            source_ids=["H01-L012"],
            quote="not allowed to question",
            explanation="Potential issue: [DEFENDANT] could not question the witness.",
            status="accepted",
        )
    ]
    kept = export.export_markdown(demo_record, rights, "R")
    assert "Maria Santos" not in kept and "[DEFENDANT]" in kept
    restored = export.export_markdown(demo_record, rights, "R", restore_names=NAMES)
    assert "Maria Santos" in restored and "[DEFENDANT]" not in restored
