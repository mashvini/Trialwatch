"""T13: the pre-submission check must catch what it claims to catch."""
from __future__ import annotations

import sys

from helpers import ROOT

sys.path.insert(0, str(ROOT))
from eval.check_submission import FORBIDDEN_PATH, SECRET  # noqa: E402


def test_secret_patterns():
    fake_groq = "gsk_" + "A1b2C3d4E5f6G7h8I9j0K1"  # built at runtime so this file never holds a key-shaped string
    fake_value = "abcdefgh" + "1234"
    assert SECRET.search(f"GROQ_API_KEY={fake_groq}")
    assert SECRET.search("GEMINI_API_KEY" + "=" + fake_value)
    assert not SECRET.search("GROQ_API_KEY=")  # the empty line in .env.example
    assert not SECRET.search(SECRET.pattern)  # the checker's own source line


def test_forbidden_paths():
    for path in [".env", "data/real_case/names.yaml", "data/demo_case/audit_log.jsonl", "data/x/.cache/a.json", "fixtures/recorded/flag.json", "data/local/my_case/case.yaml"]:
        assert FORBIDDEN_PATH.search(path), path
    for path in [".env.example", "data/demo_case/names.example.yaml", "fixtures/mock/flag.H01.json"]:
        assert not FORBIDDEN_PATH.search(path), path
