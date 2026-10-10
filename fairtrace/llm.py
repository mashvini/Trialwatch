"""One adapter for every model call.

Modes
- mock:  returns saved JSON from fixtures/mock/ (no network; tests and demo safety net)
- api:   any OpenAI-compatible endpoint (default: Groq)
- local: Ollama on this machine (OpenAI-compatible at http://localhost:11434/v1)

Mock lookup order, given the case id: fixtures/mock/<case_id>/<prompt>.<mock_key>.json, then
fixtures/mock/<case_id>/<prompt>.json. Only the demo case (and calls without a case id, as in the
tests) also looks at those names directly under fixtures/mock/, the shared folder holding its
outputs; any other case with no saved outputs gets a clear error instead.
Recording: with FAIRTRACE_RECORD=1, real outputs are saved to fixtures/recorded/<case_id>/ under
the same names, so good runs can be copied into fixtures/mock/<case_id>/ for the demo.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from .config import VALID_MODES, Settings

T = TypeVar("T", bound=BaseModel)

# The case whose outputs live directly in fixtures/mock/ (data/demo_case/). Every other case keeps
# its own in fixtures/mock/<case_id>/.
SHARED_FIXTURES_CASE = "demo_synthetic"


class LLMError(RuntimeError):
    """A model call failed in a way the user should see (missing key, bad JSON, ...)."""


def extract_json(text: str) -> Any:
    """Parse JSON even if the model wrapped it in ``` fences or added a sentence around it."""
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fenced:
        text = fenced.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        starts = [i for i in (text.find("{"), text.find("[")) if i != -1]
        end = max(text.rfind("}"), text.rfind("]"))
        if not starts or end == -1:
            raise
        return json.loads(text[min(starts): end + 1])


class LLM:
    def __init__(self, settings: Settings, mode: str | None = None, case_id: str | None = None):
        self.settings = settings
        self.mode = mode or settings.mode
        # Fixtures and recordings are looked up per case first, so two cases' "H01" never collide.
        self.case_id = case_id
        if self.mode not in VALID_MODES:
            raise LLMError(f"Unknown mode {self.mode!r}: use mock, api or local")
        self._client = None

    @property
    def model_name(self) -> str:
        return "mock" if self.mode == "mock" else self.settings.providers[self.mode].model

    # ------------------------------------------------------------ public API
    def complete_json(self, prompt_name: str, system: str, user: str, mock_key: str | None = None) -> Any:
        """Run one prompt and return parsed JSON."""
        if self.mode == "mock":
            return self._mock(prompt_name, mock_key)

        provider = self.settings.providers[self.mode]
        messages = [{"role": "system", "content": system}, {"role": "user", "content": user}]
        kwargs: dict[str, Any] = {
            "model": provider.model,
            "messages": messages,
            "temperature": self.settings.generation.get("temperature", 0),
        }
        if provider.json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        last_error: Exception | None = None
        for _ in range(1 + int(self.settings.generation.get("max_retries", 1))):
            response = self._client_for(provider).chat.completions.create(**kwargs)
            text = response.choices[0].message.content or ""
            try:
                data = extract_json(text)
            except (json.JSONDecodeError, ValueError) as e:
                last_error = e
                messages += [
                    {"role": "assistant", "content": text},
                    {"role": "user", "content": f"That was not valid JSON ({e}). Reply with JSON only."},
                ]
                continue
            self._record(prompt_name, mock_key, data)
            return data
        raise LLMError(f"{prompt_name}: the model did not return valid JSON ({last_error})")

    def complete_model(
        self,
        prompt_name: str,
        system: str,
        user: str,
        model: type[T],
        key: str | None = None,
        mock_key: str | None = None,
    ) -> list[T]:
        """Run one prompt and validate the result as a list of `model` objects.

        `key` picks the list out of a JSON object, e.g. {"flags": [...]} with key="flags".
        """
        data = self.complete_json(prompt_name, system, user, mock_key=mock_key)
        if key is not None and isinstance(data, dict):
            data = data.get(key, [])
        if isinstance(data, dict):
            data = [data]
        try:
            return [model.model_validate(item) for item in data]
        except ValidationError as e:
            raise LLMError(f"{prompt_name}: output did not match {model.__name__}: {e}") from e

    # ------------------------------------------------------------ internals
    def _client_for(self, provider):
        if self._client is None:
            from openai import OpenAI  # imported lazily: mock mode needs no network client

            if not provider.is_configured:
                raise LLMError(f"Set providers.{self.mode}.model in config.yaml first")
            if not provider.api_key:
                raise LLMError(f"Missing API key: set {provider.api_key_env} in .env")
            self._client = OpenAI(
                base_url=provider.base_url,
                api_key=provider.api_key,
                timeout=self.settings.generation.get("timeout_s", 60),
            )
        return self._client

    def _mock(self, prompt_name: str, mock_key: str | None) -> Any:
        root = self.settings.path("fixtures_dir")
        # The shared folder holds the demo case's outputs. Another case never falls back to it:
        # replaying the demo's outputs on a different case would show invented citations.
        uses_shared = self.case_id in (None, SHARED_FIXTURES_CASE)
        folders = ([root / self.case_id] if self.case_id else []) + ([root] if uses_shared else [])
        candidates = [
            path
            for folder in folders
            for path in ([folder / f"{prompt_name}.{mock_key}.json"] if mock_key else []) + [folder / f"{prompt_name}.json"]
        ]
        for path in candidates:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        if not uses_shared and not (root / self.case_id).exists():
            raise LLMError(
                f"Case {self.case_id!r} has no saved outputs for mock mode: use api or local mode, "
                f"or record a run into fixtures/mock/{self.case_id}/ (FAIRTRACE_RECORD=1)"
            )
        names = ", ".join(p.name for p in candidates)
        raise LLMError(f"No mock fixture for {prompt_name!r} (looked for {names})")

    def _record(self, prompt_name: str, mock_key: str | None, data: Any) -> None:
        if os.getenv("FAIRTRACE_RECORD") != "1":
            return
        folder = self.settings.path("record_dir") / (self.case_id or "")
        folder.mkdir(parents=True, exist_ok=True)
        name = f"{prompt_name}.{mock_key}.json" if mock_key else f"{prompt_name}.json"
        (folder / name).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
