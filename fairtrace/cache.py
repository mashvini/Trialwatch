"""Cache module results so that ticking a module on and off never repeats model calls.

The key covers the module, the model mode, the prompt version, the module's settings and its
inputs, so any real change produces a fresh run. Files live in data/<case>/.cache/.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel


def cache_key(analyzer, record, settings, mode: str) -> str:
    payload = {
        "analyzer": analyzer.id,
        "mode": mode,
        "prompt": settings.prompt_versions.get(analyzer.id, ""),
        "params": analyzer.params(settings),
        "inputs": analyzer.cache_inputs(record),
    }
    blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def get_or_run(analyzer, record, settings, llm, case_dir: Path) -> BaseModel:
    path = Path(case_dir) / ".cache" / f"{analyzer.id}-{cache_key(analyzer, record, settings, llm.mode)}.json"
    if path.exists():
        return analyzer.result_model.model_validate_json(path.read_text(encoding="utf-8"))
    result = analyzer.run(record, settings, llm)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return result
