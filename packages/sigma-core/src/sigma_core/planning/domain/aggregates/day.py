from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Final

from sigma_core.planning.domain.entities.time_block import TimeBlock
from sigma_core.planning.domain.errors import (
    BlockNotFoundError,
    BlockOverlapError,
    InvalidTimeBlockError,
)
from sigma_core.planning.domain.value_objects import BlockId, DayId
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp


MAX_BLOCKS_PER_DAY = 48


class _Unset:
    """Sentinel para distinguir 'no pasado' de 'None explícito' en update_block."""

    _instance: _Unset | None = None

    def __new__(cls) -> _Unset:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "<UNSET>"


UNSET: Final[_Unset] = _Unset()


@dataclass
class Day:
    """Día calendario de un Space con sus `TimeBlock` asignados.

    Invariantes:
    - Los bloques pertenecen a `self.date` (compara día calendario de `start_at`).
    - Los bloques no se solapan entre sí (intervalos semi-abiertos).
    - Hay como máximo `MAX_BLOCKS_PER_DAY` bloques.
    - Los bloques se mantienen ordenados por `start_at` tras cada mutación.
    """

    id: DayId
    space_id: SpaceId
    date: date
    blocks: list[TimeBlock] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)

    # ── Mutations ───────────────────────────────────────────────

    def add_block(self, block: TimeBlock) -> None:
        if len(self.blocks) >= MAX_BLOCKS_PER_DAY:
            raise InvalidTimeBlockError(
                f"Day {self.id.value} already holds {MAX_BLOCKS_PER_DAY} blocks"
            )
        self._ensure_block_belongs_to_day(block)
        self._ensure_no_overlap(block, exclude_id=None)
        self.blocks.append(block)
        self._sort_blocks()
        self._touch()

    def remove_block(self, block_id: BlockId) -> None:
        target = self._find_block(block_id)
        self.blocks.remove(target)
        self._touch()

    def update_block(
        self,
        block_id: BlockId,
        *,
        start_at: Timestamp | None = None,
        duration: Minutes | None = None,
        area_id: AreaId | None | _Unset = UNSET,
        notes: str | None = None,
    ) -> None:
        current = self._find_block(block_id)
        new_start = start_at if start_at is not None else current.start_at
        new_duration = duration if duration is not None else current.duration
        new_area: AreaId | None = (
            current.area_id if isinstance(area_id, _Unset) else area_id
        )
        new_notes = notes if notes is not None else current.notes

        replacement = TimeBlock(
            id=current.id,
            start_at=new_start,
            duration=new_duration,
            area_id=new_area,
            notes=new_notes,
        )
        self._ensure_block_belongs_to_day(replacement)
        self._ensure_no_overlap(replacement, exclude_id=current.id)

        idx = self.blocks.index(current)
        self.blocks[idx] = replacement
        self._sort_blocks()
        self._touch()

    def clear_blocks(self) -> None:
        if not self.blocks:
            return
        self.blocks.clear()
        self._touch()

    # ── Internal helpers ────────────────────────────────────────

    def _find_block(self, block_id: BlockId) -> TimeBlock:
        for b in self.blocks:
            if b.id == block_id:
                return b
        raise BlockNotFoundError(
            f"Block {block_id.value} not found in day {self.id.value}"
        )

    def _ensure_block_belongs_to_day(self, block: TimeBlock) -> None:
        if block.start_at.value.date() != self.date:
            raise InvalidTimeBlockError(
                f"Block start_at {block.start_at.value.date()} "
                f"does not match day {self.date}"
            )

    def _ensure_no_overlap(
        self, block: TimeBlock, *, exclude_id: BlockId | None
    ) -> None:
        for existing in self.blocks:
            if exclude_id is not None and existing.id == exclude_id:
                continue
            if existing.overlaps(block):
                raise BlockOverlapError(block_id=existing.id.value)

    def _sort_blocks(self) -> None:
        self.blocks.sort(key=lambda b: b.start_at.value)

    def _touch(self) -> None:
        self.updated_at = Timestamp.now()
