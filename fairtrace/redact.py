"""Replace real names with roles before any model call (and restore them only on export).

The map lives in data/<case>/names.yaml (git-ignored), e.g.:
    "Maria Santos": DEFENDANT
Limitation: it only catches names you list.
"""
from __future__ import annotations

from pathlib import Path

import yaml


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
    raise NotImplementedError("T11: redact names (see the docstring in redact.py)")


def restore(text: str, mapping: dict[str, str]) -> str:
    """T11. Reverse of redact(): "[ROLE]" -> the original name (use only at export, if the lawyer chooses)."""
    raise NotImplementedError("T11: restore names (see the docstring in redact.py)")
