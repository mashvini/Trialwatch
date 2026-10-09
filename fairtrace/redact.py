"""Replace real names with roles before any model call (and restore them only on export).

The map lives in data/<case>/names.yaml (git-ignored), e.g.:
    "Maria Santos": DEFENDANT
Limitation: it only catches names you list.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

from .schemas import SourceLine


def load_names(case_dir: Path) -> dict[str, str]:
    """Return {real name: role} from names.yaml, or {} if the case has none."""
    path = Path(case_dir) / "names.yaml"
    if not path.exists():
        return {}
    return {str(k): str(v) for k, v in (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).items()}


def redact(text: str, mapping: dict[str, str]) -> str:
    """T11. Replace each name with "[ROLE]".

    Spec (tests/test_spec_redact.py):
    - Whole words only ("Maria" must not change "Mariana"), case-insensitive.
    - Longest names first, so "Maria Santos" is replaced before "Maria".
    """
    if not mapping:
        return text
    roles = {name.lower(): role for name, role in mapping.items()}
    names = sorted(mapping, key=len, reverse=True)
    # One pass over the text, so a replacement like "[DEFENDANT]" is never matched again.
    pattern = re.compile(r"(?<!\w)(" + "|".join(re.escape(n) for n in names) + r")(?!\w)", re.IGNORECASE)
    return pattern.sub(lambda m: f"[{roles[m.group(1).lower()]}]", text)


def restore(text: str, mapping: dict[str, str]) -> str:
    """T11. Reverse of redact(): "[ROLE]" -> the original name (use only at export, if the lawyer chooses)."""
    for name, role in mapping.items():
        text = text.replace(f"[{role}]", name)
    return text


def redact_lines(lines: list[SourceLine], mapping: dict[str, str]) -> list[SourceLine]:
    """Redact numbered lines right after ingest, keeping their IDs.

    Doing it here, not per prompt, means the model, the verifier, Copy-Through and the app all see
    the same text, so a quote of "[DEFENDANT]" still matches its cited line.
    """
    return [line.model_copy(update={"text": redact(line.text, mapping)}) for line in lines]
