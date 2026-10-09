"""Tests for the plumbing that already works. These must always pass."""
from __future__ import annotations

import json

import pytest
from helpers import DEMO, oracle_lines

from fairtrace import ingest, review
from fairtrace.analyzers import REGISTRY, in_stage_order
from fairtrace.analyzers.base import Analyzer
from fairtrace.cache import get_or_run
from fairtrace.evaluate import load_answer_key
from fairtrace.llm import LLM, LLMError, extract_json
from fairtrace.prompts import load_prompt, render
from fairtrace.schemas import Case, CaseRecord, Challenge, ChallengeSet, Decision, Event, Flag


def test_settings_load(settings):
    assert settings.mode in ("mock", "api", "local")
    assert settings.path("rights_file").exists()


def test_demo_case_loads():
    case = ingest.load_case(DEMO)
    assert case.synthetic
    assert [h.id for h in case.hearings] == ["H01", "H02"]
    judgment = next(d for d in case.documents if d.type == "judgment")
    assert judgment.reasoning_paragraphs == (3, 4)


def test_rights_load_with_unique_ids(rights):
    ids = [r.id for r in rights]
    assert len(ids) == len(set(ids))
    assert {"examine_witnesses", "reasoned_judgment", "public_hearing"} <= set(ids)


def test_copy_through_right_exists(settings, rights):
    assert settings.copy_through["right_id"] in {r.id for r in rights}


def test_prompts_load_and_render(settings):
    for name in ("extract", "flag", "devils_advocate"):
        system, user, version = load_prompt(settings, name)
        assert system and user and version == "v1"
    _, user, _ = load_prompt(settings, "extract")
    filled = render(user, hearing_id="H01", lines="H01-L005 | text")
    assert "{{" not in filled and "H01-L005" in filled


def test_render_refuses_a_missing_placeholder():
    with pytest.raises(KeyError):
        render("Hello {{name}}")


def test_modules_run_in_stage_order():
    assert set(REGISTRY) == {"copy_through", "devils_advocate"}
    order = [a.id for a in in_stage_order(["devils_advocate", "copy_through", "unknown"])]
    assert order == ["copy_through", "devils_advocate"]


def test_modules_explain_why_they_cannot_run():
    empty = CaseRecord(case=ingest.load_case(DEMO))
    ok, reason = REGISTRY["copy_through"].available(empty)
    assert not ok and "T1" in reason
    ok, reason = REGISTRY["devils_advocate"].available(empty)
    assert not ok and reason
    no_judgment = CaseRecord(case=Case(id="x", title="x", country="x"))
    assert not REGISTRY["copy_through"].available(no_judgment)[0]


def test_copy_through_available_once_sources_exist(demo_record):
    assert REGISTRY["copy_through"].available(demo_record) == (True, "")


def test_mock_llm_returns_fixtures(settings):
    llm = LLM(settings, "mock")
    events = llm.complete_model("extract", "system", "user", Event, key="events", mock_key="H01")
    assert events and all(e.hearing == "H01" for e in events)
    assert llm.complete_model("flag", "system", "user", Flag, key="flags", mock_key="H02") == []


def test_mock_llm_missing_fixture_is_a_clear_error(settings):
    with pytest.raises(LLMError):
        LLM(settings, "mock").complete_json("no_such_prompt", "system", "user")


def test_unknown_mode_rejected(settings):
    with pytest.raises(LLMError):
        LLM(settings, "cloud")


def test_extract_json_handles_fences_and_prose():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json('Here you go: {"a": [1, 2]} hope that helps') == {"a": [1, 2]}


def test_fixtures_match_schemas(settings):
    folder = settings.path("fixtures_dir")
    for path in folder.glob("extract.*.json"):
        [Event.model_validate(e) for e in json.loads(path.read_text(encoding="utf-8"))["events"]]
    for path in folder.glob("flag.*.json"):
        [Flag.model_validate(f) for f in json.loads(path.read_text(encoding="utf-8"))["flags"]]
    data = json.loads((folder / "devils_advocate.json").read_text(encoding="utf-8"))
    [Challenge.model_validate(c) for c in data["challenges"]]


def test_fixture_citations_point_to_real_lines(settings):
    """Every citation in the fixtures exists, except the deliberate bad one (see fixtures/README.md)."""
    ids = {line.id for line in oracle_lines()}
    deliberate = {"H01-L099"}
    for path in settings.path("fixtures_dir").glob("*.json"):
        for items in json.loads(path.read_text(encoding="utf-8")).values():
            for item in items:
                for sid in item.get("source_ids", []):
                    assert sid in ids or sid in deliberate, f"{path.name} cites unknown line {sid}"


def test_answer_key_points_to_real_lines():
    key = load_answer_key(DEMO)
    ids = {line.id for line in oracle_lines()}
    for item in key.expected:
        assert set(item.source_ids) <= ids, item.id


def test_audit_log_latest_decision_wins(tmp_path):
    flags = [Flag(id="F1", right_id="examine_witnesses", source_ids=["H01-L012"], quote="q", explanation="e")]
    review.record_decision(tmp_path, Decision(flag_id="F1", decision="accepted", reviewer="A"))
    review.record_decision(tmp_path, Decision(flag_id="F1", decision="needs_facts", reviewer="B"))
    review.apply_decisions(flags, review.load_decisions(tmp_path))
    assert flags[0].status == "needs_facts"
    assert len(review.load_decisions(tmp_path)) == 2  # history is kept


class _CountingModule(Analyzer):
    id = "counting"
    label = "Counting"
    description = "test module"
    stage = 2
    uses_model = False
    result_model = ChallengeSet

    def __init__(self):
        self.calls = 0

    def available(self, record):
        return True, ""

    def run(self, record, settings, llm):
        self.calls += 1
        return ChallengeSet()


def test_cache_avoids_repeat_runs(settings, tmp_path, demo_record):
    module, llm = _CountingModule(), LLM(settings, "mock")
    get_or_run(module, demo_record, settings, llm, tmp_path)
    get_or_run(module, demo_record, settings, llm, tmp_path)
    assert module.calls == 1
    demo_record.flags.append(Flag(id="F9", right_id="interpreter", source_ids=["H01-L005"], quote="q", explanation="e"))
    get_or_run(module, demo_record, settings, llm, tmp_path)
    assert module.calls == 2  # new inputs, new run
