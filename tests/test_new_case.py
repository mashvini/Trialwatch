"""The "Add a case" tab's plain-code half: validation and writing the case folder."""
from __future__ import annotations

from fairtrace import ingest, new_case, redact
from fairtrace.new_case import DocumentUpload, NewCase, Upload

NOTES = "# Hearing 1\n\n09:05 Hearing opened.\n09:10 Defense counsel asked for time to prepare.\n"
JUDGMENT = "The court heard the case.\n\nThe court finds the defendant liable.\n"


def _new(**overrides) -> NewCase:
    base = dict(title="Testland: case of a reporter", country="Testland", kind="synthetic", hearings=[Upload(name="h1.txt", text=NOTES)])
    base.update(overrides)
    return NewCase(**base)


def test_written_case_loads_and_numbers_like_any_other(tmp_path):
    folder = new_case.write_case(tmp_path, _new(
        hearing_dates=["2026-03-02"],
        documents=[DocumentUpload(name="j.txt", text=JUDGMENT, id="JDG", type="judgment", reasoning_paragraphs=(2, 2))],
        names='"Maria Santos": DEFENDANT',
    ))
    assert folder == tmp_path / "local" / "testland_case_of_a_reporter"
    case = ingest.load_case(folder)
    assert case.id == "local_testland_case_of_a_reporter" and case.synthetic
    assert case.hearings[0].date == "2026-03-02" and case.documents[0].reasoning_paragraphs == (2, 2)
    ids = [line.id for line in ingest.read_sources(folder, case)]
    assert ids == ["H01-L003", "H01-L004", "JDG-P001", "JDG-P002"]  # physical line numbers kept
    assert redact.load_names(folder) == {"Maria Santos": "DEFENDANT"}
    assert new_case.local_cases(tmp_path) == [folder]


def test_never_overwrites_an_existing_case(tmp_path):
    first = new_case.write_case(tmp_path, _new())
    second = new_case.write_case(tmp_path, _new())
    assert first != second and second.name.endswith("_2")


def test_reconstructed_case_carries_its_source(tmp_path):
    folder = new_case.write_case(tmp_path, _new(kind="reconstructed", source="https://example.org/report"))
    case = ingest.load_case(folder)
    assert not case.synthetic and "https://example.org/report" in case.provenance


def test_problems_are_reported_in_plain_words():
    assert new_case.problems(_new()) == []
    assert new_case.problems(_new(title="", hearings=[]))  # title and hearings missing
    assert new_case.problems(_new(kind="reconstructed"))  # no source
    assert new_case.problems(_new(hearing_dates=["2 March"]))
    judgment = DocumentUpload(name="j.txt", text=JUDGMENT, id="JDG", type="judgment", reasoning_paragraphs=(1, 5))
    assert any("reasoning range" in p for p in new_case.problems(_new(documents=[judgment])))
    twice = [DocumentUpload(name=n, text=JUDGMENT, id="DOC", type="other") for n in ("a.txt", "b.txt")]
    assert any("own prefix" in p for p in new_case.problems(_new(documents=twice)))
    assert new_case.problems(_new(names="just some words"))


def test_non_utf8_upload_is_a_visible_error():
    assert new_case.decode("﻿Notes".encode("utf-8")) == "Notes"
    try:
        new_case.decode("café".encode("latin-1"))
    except ValueError as e:
        assert "UTF-8" in str(e)
    else:
        raise AssertionError("expected a ValueError")
