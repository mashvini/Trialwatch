from __future__ import annotations

import json

import pytest
from helpers import DEMO, oracle_lines

from fairtrace import ingest
from fairtrace.config import load_settings
from fairtrace.schemas import CaseRecord, Flag
from fairtrace.taxonomy import load_rights


@pytest.fixture(scope="session")
def settings():
    return load_settings()


@pytest.fixture(scope="session")
def rights(settings):
    return load_rights(settings)


@pytest.fixture
def demo_record() -> CaseRecord:
    """The synthetic demo case with reference numbering (independent of T1)."""
    return CaseRecord(case=ingest.load_case(DEMO), source_lines=oracle_lines())


@pytest.fixture
def fixture_flags(settings) -> list[Flag]:
    """Flags from the mock fixture for H01, minus the planted mistake F-H01-6 (the verifier rejects it)."""
    data = json.loads((settings.path("fixtures_dir") / "flag.H01.json").read_text(encoding="utf-8"))
    return [Flag.model_validate(f) for f in data["flags"] if f["id"] != "F-H01-6"]
