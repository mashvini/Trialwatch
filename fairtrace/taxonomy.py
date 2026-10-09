"""Load the rights list and worked examples that lawyers maintain in taxonomy/."""
from __future__ import annotations

import yaml
from pydantic import BaseModel

from .config import Settings


class Right(BaseModel):
    id: str                          # never rename once tests or answer keys use it
    name: str
    basis: str                       # treaty article and General Comment
    observable_in_court: bool = True
    status: str = "draft"            # draft | reviewed
    red_flags: list[str] = []
    key_questions: list[str] = []
    regional_references: list[str] = []
    notes: str = ""


def load_rights(settings: Settings) -> list[Right]:
    data = yaml.safe_load(settings.path("rights_file").read_text(encoding="utf-8")) or []
    rights = [Right.model_validate(item) for item in data]
    ids = [r.id for r in rights]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise ValueError(f"Duplicate right ids in rights.yaml: {duplicates}")
    return rights


def rights_for_prompt(rights: list[Right]) -> str:
    """Compact text block describing the rights, for prompts."""
    blocks = []
    for r in rights:
        blocks.append(
            f"- id: {r.id}\n"
            f"  name: {r.name}\n"
            f"  basis: {r.basis}\n"
            f"  red flags: {'; '.join(r.red_flags)}\n"
            f"  key questions: {'; '.join(r.key_questions)}"
        )
    return "\n".join(blocks)


def load_worked_examples(settings: Settings) -> str:
    """The worked examples file as text, inserted into the flag prompt as-is."""
    path = settings.path("examples_file")
    return path.read_text(encoding="utf-8") if path.exists() else ""
