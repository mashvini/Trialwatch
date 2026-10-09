"""Switchable modules. The sidebar shows one checkbox per entry in REGISTRY."""
from __future__ import annotations

from .base import Analyzer
from .copy_through import CopyThrough
from .devils_advocate import DevilsAdvocate

REGISTRY: dict[str, Analyzer] = {a.id: a for a in (CopyThrough(), DevilsAdvocate())}


def in_stage_order(ids: list[str]) -> list[Analyzer]:
    """Enabled modules, producers (stage 1) before challengers (stage 2). Unknown ids are ignored."""
    return sorted((REGISTRY[i] for i in ids if i in REGISTRY), key=lambda a: a.stage)


__all__ = ["Analyzer", "REGISTRY", "in_stage_order", "CopyThrough", "DevilsAdvocate"]
