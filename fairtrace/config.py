"""Load config.yaml and .env into one Settings object.

Secrets (API keys) come only from environment variables / .env, never from config.yaml.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
VALID_MODES = ("mock", "api", "local")


@dataclass
class ProviderSettings:
    """One OpenAI-compatible endpoint (Groq, Ollama, ...)."""

    base_url: str
    model: str
    api_key_env: str = ""
    json_mode: bool = False

    @property
    def api_key(self) -> str:
        if not self.api_key_env:
            return "not-needed"  # Ollama ignores the key, but the client requires one
        return os.getenv(self.api_key_env, "")

    @property
    def is_configured(self) -> bool:
        return "<" not in self.model and bool(self.model)


@dataclass
class Settings:
    mode: str
    providers: dict[str, ProviderSettings]
    generation: dict
    prompt_versions: dict[str, str]
    analyzers_enabled: list[str]
    copy_through: dict
    verify: dict
    paths: dict
    root: Path = ROOT

    def path(self, key: str) -> Path:
        """Absolute path for a key under `paths:` in config.yaml."""
        return self.root / self.paths[key]


def load_settings(config_path: Path | None = None) -> Settings:
    load_dotenv(ROOT / ".env")
    raw = yaml.safe_load((config_path or ROOT / "config.yaml").read_text(encoding="utf-8"))
    mode = os.getenv("FAIRTRACE_MODE") or raw.get("mode", "mock")
    if mode not in VALID_MODES:
        mode = "mock"
    return Settings(
        mode=mode,
        providers={name: ProviderSettings(**p) for name, p in raw["providers"].items()},
        generation=raw.get("generation", {}),
        prompt_versions=raw.get("prompt_versions", {}),
        analyzers_enabled=raw.get("analyzers", {}).get("enabled", []),
        copy_through=raw.get("copy_through", {}),
        verify=raw.get("verify", {}),
        paths=raw["paths"],
    )
