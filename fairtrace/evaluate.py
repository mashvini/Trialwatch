"""Measure flags against a lawyer-written answer key (data/<case>/answer_key.yaml)."""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel

from .schemas import Flag


class AnswerItem(BaseModel):
    id: str
    right_id: str
    source_ids: list[str]
    note: str = ""
    detectable_by_mvp: bool = True     # False = needs analysis we haven't built; not counted in recall


class AnswerKey(BaseModel):
    case_id: str
    expected: list[AnswerItem] = []
    clean_hearings: list[str] = []     # any flag citing these hearings is a false alarm


def load_answer_key(case_dir: Path) -> AnswerKey | None:
    path = Path(case_dir) / "answer_key.yaml"
    if not path.exists():
        return None
    return AnswerKey.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def evaluate(flags: list[Flag], key: AnswerKey, line_ids: set[str]) -> dict:
    """T10. Score flags against the answer key.

    Spec (tests/test_spec_evaluate.py):
    - An expected item is "caught" if any flag has the same right_id and shares >= 1 source id.
    - recall = caught / number of expected items with detectable_by_mvp=True (0.0 if none);
      only detectable items count toward caught and missed.
    - false_alarms = number of flags citing any line of a clean hearing (id starts with "<hearing>-L").
    - citation_rate = share of flags whose source_ids all exist in line_ids (1.0 if no flags).
    Return:
      {"caught": [item ids], "missed": [item ids], "recall": float,
       "false_alarms": int, "citation_rate": float, "flags_total": int,
       "not_detectable": [item ids with detectable_by_mvp=False]}
    """
    raise NotImplementedError("T10: evaluation (see the docstring in evaluate.py)")
