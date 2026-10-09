"""The interface every switchable module implements.

Stage 1 modules produce flags (Copy-Through); stage 2 modules challenge flags (Devil's Advocate).
The app runs enabled modules in stage order, shows `available()`'s reason when a module can't
run, and caches results (fairtrace/cache.py) so toggling a module never repeats model calls.

Adding a module: subclass Analyzer, add an instance to REGISTRY in analyzers/__init__.py,
and add a renderer in app.py.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import ClassVar

from pydantic import BaseModel

from ..config import Settings
from ..schemas import CaseRecord


class Analyzer(ABC):
    id: ClassVar[str]
    label: ClassVar[str]
    description: ClassVar[str]
    stage: ClassVar[int]                      # 1 = produces flags, 2 = challenges flags
    uses_model: ClassVar[bool]
    result_model: ClassVar[type[BaseModel]]   # what run() returns (and the cache stores)

    @abstractmethod
    def available(self, record: CaseRecord) -> tuple[bool, str]:
        """(True, "") if the module can run on this record; otherwise (False, reason for the user)."""

    @abstractmethod
    def run(self, record: CaseRecord, settings: Settings, llm) -> BaseModel:
        """Do the work and return an instance of result_model. Must not modify the record."""

    def apply(self, record: CaseRecord, result: BaseModel, settings: Settings) -> None:
        """Merge the result into the record (add flags, attach challenges...). Default: nothing."""

    def cache_inputs(self, record: CaseRecord) -> object:
        """What the cache key is built from. Review status is excluded on purpose."""
        return {
            "lines": [line.model_dump() for line in record.source_lines],
            "flags": [f.model_dump(exclude={"status", "verifier_notes"}) for f in record.flags],
        }

    def params(self, settings: Settings) -> dict:
        """Module settings that should invalidate the cache when they change."""
        return {}
