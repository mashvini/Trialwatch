"""Load versioned prompt files and fill their {{placeholders}}.

A prompt file (prompts/<name>_<version>.md) has two sections, "## System" and "## User".
Placeholders look like {{lines}}. Single braces (e.g. JSON examples) are left alone.
"""
from __future__ import annotations

import re

from .config import Settings
from .schemas import SourceLine

_SECTION = re.compile(r"^## (System|User)\s*$", re.M)
_PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


def load_prompt(settings: Settings, name: str) -> tuple[str, str, str]:
    """Return (system, user_template, version) for a prompt name like "flag"."""
    version = settings.prompt_versions.get(name, "v1")
    path = settings.path("prompts_dir") / f"{name}_{version}.md"
    parts = _SECTION.split(path.read_text(encoding="utf-8"))
    sections = {parts[i]: parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
    if "System" not in sections or "User" not in sections:
        raise ValueError(f"{path.name} needs '## System' and '## User' sections")
    return sections["System"], sections["User"], version


def render(template: str, **values: object) -> str:
    """Fill {{name}} placeholders. A placeholder without a value is an error, not a silent blank."""

    def substitute(match: re.Match) -> str:
        key = match.group(1)
        if key not in values:
            raise KeyError(f"No value given for placeholder {{{{{key}}}}}")
        return str(values[key])

    return _PLACEHOLDER.sub(substitute, template)


def format_lines(lines: list[SourceLine]) -> str:
    """Numbered lines as the model sees them: 'H01-L012 | text', one per line."""
    return "\n".join(f"{line.id} | {line.text}" for line in lines)
