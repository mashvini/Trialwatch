"""Mock fixtures are looked up per case; only the demo case uses the shared folder."""
from __future__ import annotations

import json
import sys

import pytest

from helpers import ROOT

from fairtrace import ingest
from fairtrace.llm import LLM, LLMError

sys.path.insert(0, str(ROOT))
from eval.run_eval import score  # noqa: E402

CUMPIO = ROOT / "data" / "philippines_cumpio"


def test_reconstructed_cumpio_case_runs_in_mock_mode():
    result = score(CUMPIO, "mock")
    assert result["caught"] == ["A1", "A2", "A3"] and result["not_detectable"] == ["A4"]
    assert result["rejected_by_verifier"] == [] and result["citation_rate"] == 1.0


def test_reconstructed_case_is_labeled_and_cites_its_source():
    case = ingest.load_case(CUMPIO)
    assert not case.synthetic and case.provenance
    assert "hri.law.columbia.edu" in (CUMPIO / "case.yaml").read_text(encoding="utf-8")
    for path in (CUMPIO / "hearings").glob("*.txt"):
        assert path.read_text(encoding="utf-8").startswith("# RECONSTRUCTED"), path.name


def test_case_folder_wins_over_the_shared_folder(settings, tmp_path, monkeypatch):
    shared, own = tmp_path, tmp_path / "case_x"
    own.mkdir()
    (shared / "flag.H01.json").write_text(json.dumps({"flags": ["shared"]}), encoding="utf-8")
    (own / "flag.H01.json").write_text(json.dumps({"flags": ["own"]}), encoding="utf-8")
    original = settings.path
    monkeypatch.setattr(settings, "path", lambda key: tmp_path if key == "fixtures_dir" else original(key))
    assert LLM(settings, "mock", case_id="case_x").complete_json("flag", "s", "u", mock_key="H01") == {"flags": ["own"]}
    assert LLM(settings, "mock", case_id="demo_synthetic").complete_json("flag", "s", "u", mock_key="H01") == {"flags": ["shared"]}
    assert LLM(settings, "mock").complete_json("flag", "s", "u", mock_key="H01") == {"flags": ["shared"]}
    # Any other case never replays the demo's outputs: a clear error instead.
    with pytest.raises(LLMError, match="no saved outputs"):
        LLM(settings, "mock", case_id="other").complete_json("flag", "s", "u", mock_key="H01")
