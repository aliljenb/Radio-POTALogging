"""Outbound port for turning submitted QSOs into ADIF-formatted text."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from .value_objects import Qso


class AdifExporter(Protocol):
    def export(self, qsos: Sequence[Qso]) -> str:
        """Return ADIF-formatted text for the given QSOs. Pure string transform, no I/O."""
        ...
