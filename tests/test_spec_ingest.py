"""Spec for T1 (ingest). Skips until number_hearing / split_paragraphs are built."""
from __future__ import annotations

from helpers import DEMO, implemented_or_skip, oracle_lines

from fairtrace import ingest
from fairtrace.schemas import DocumentRef, HearingRef


def test_hearing_ids_use_physical_line_numbers():
    text = "# comment\n\nFirst line\nSecond line   \n"
    lines = implemented_or_skip(ingest.number_hearing, HearingRef(id="H03", file="x.txt"), text)
    assert [line.id for line in lines] == ["H03-L003", "H03-L004"]
    assert lines[1].text == "Second line"
    assert {line.doc for line in lines} == {"H03"}


def test_document_paragraphs():
    text = "# comment\n\nPara one\ncontinues   here.\n\n\nPara two.\n"
    paragraphs = implemented_or_skip(
        ingest.split_paragraphs, DocumentRef(id="JDG", type="judgment", file="x.txt"), text
    )
    assert [p.id for p in paragraphs] == ["JDG-P001", "JDG-P002"]
    assert paragraphs[0].text == "Para one continues here."
    assert {p.doc for p in paragraphs} == {"JDG"}


def test_demo_case_matches_the_reference_numbering():
    case = ingest.load_case(DEMO)
    lines = implemented_or_skip(ingest.read_sources, DEMO, case)
    assert [(line.id, line.text) for line in lines] == [(line.id, line.text) for line in oracle_lines()]
