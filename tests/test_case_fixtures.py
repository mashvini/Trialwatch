"""Mock fixtures are looked up per case first, then in the shared folder the demo case uses."""
from __future__ import annotations

import json

from fairtrace.llm import LLM


def test_case_folder_wins_over_the_shared_folder(settings, tmp_path, monkeypatch):
    shared, own = tmp_path, tmp_path / "case_x"
    own.mkdir()
    (shared / "flag.H01.json").write_text(json.dumps({"flags": ["shared"]}), encoding="utf-8")
    (own / "flag.H01.json").write_text(json.dumps({"flags": ["own"]}), encoding="utf-8")
    original = settings.path
    monkeypatch.setattr(settings, "path", lambda key: tmp_path if key == "fixtures_dir" else original(key))
    assert LLM(settings, "mock", case_id="case_x").complete_json("flag", "s", "u", mock_key="H01") == {"flags": ["own"]}
    assert LLM(settings, "mock", case_id="other").complete_json("flag", "s", "u", mock_key="H01") == {"flags": ["shared"]}
    assert LLM(settings, "mock").complete_json("flag", "s", "u", mock_key="H01") == {"flags": ["shared"]}
