from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final

from sigma_core.planning.domain.entities.day_template_block import (
    DayTemplateBlock,
)
from sigma_core.planning.domain.errors import (
    BlockNotFoundError,
    BlockOverlapError,
    InvalidTimeBlockError,
)
from sigma_core.planning.domain.value_objects import (
    BlockId,
    DayTemplateId,
    TimeOfDay,
)
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp


MAX_BLOCKS_PER_TEMPLATE: Final[int] = 48
MINUTES_PER_DAY: Final[int] = 24 * 60


class _Unset:
    _instance: _Unset | None = None

    def __new__(cls) -> _Unset:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "<UNSET>"


UNSET: Final[_Unset] = _Unset()


@dataclass
class DayTemplate:
    """Plantilla de día con bloques relativos (`TimeOfDay` + duración).

    Invariantes:
    - Los bloques no se solapan entre sí (en minutos-del-día).
    - Ningún bloque hace wraparound a medianoche (`start + duration <= 1440`).
    - Máximo `MAX_BLOCKS_PER_TEMPLATE` bloques.
    - Se mantienen ordenados por `start_at`.
    """

    id: DayTemplateId
    space_id: SpaceId
    name: str
    blocks: list[DayTemplateBlock] = field(default_factory=list)
    created_at: Timestamp = field(default_factory=Timestamp.now)
    updated_at: Timestamp = field(default_factory=Timestamp.now)

    def add_block(self, block: DayTemplateBlock) -> None:
        if len(self.blocks) >= MAX_BLOCKS_PER_TEMPLATE:
            raise InvalidTimeBlockError(
                f"DayTemplate {self.id.value} already holds "
                f"{MAX_BLOCKS_PER_TEMPLATE} blocks"
            )
        self._ensure_no_wraparound(block)
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
        start_at: TimeOfDay | None = None,
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

        replacement = DayTemplateBlock(
            id=current.id,
            start_at=new_start,
            duration=new_duration,
            area_id=new_area,
            notes=new_notes,
        )
        self._ensure_no_wraparound(replacement)
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

    def rename(self, name: str) -> None:
        self.name = name
        self._touch()

    def replace_blocks(self, blocks: list[DayTemplateBlock]) -> None:
        """Reemplaza atómicamente la lista completa de bloques validando todo."""
        self._assign_validated_blocks(blocks)
        self._touch()

    def rehydrate_blocks(self, blocks: list[DayTemplateBlock]) -> None:
        """Asigna bloques validados SIN bumpear ``updated_at``.

        Uso exclusivo de los mappers al rehidratar desde persistencia: los
        mismos invariantes que ``replace_blocks`` deben cumplirse (el mapper
        es el último guardián contra datos corruptos en Firestore), pero la
        marca temporal no debe modificarse en una operación de lectura.
        """
        self._assign_validated_blocks(blocks)

    def _assign_validated_blocks(
        self, blocks: list[DayTemplateBlock]
    ) -> None:
        if len(blocks) > MAX_BLOCKS_PER_TEMPLATE:
            raise InvalidTimeBlockError(
                f"DayTemplate {self.id.value} exceeds "
                f"{MAX_BLOCKS_PER_TEMPLATE} blocks"
            )
        # Validar individualmente y contra los ya procesados
        validated: list[DayTemplateBlock] = []
        for block in blocks:
            self._ensure_no_wraparound(block)
            for existing in validated:
                if existing.overlaps(block):
                    raise BlockOverlapError(block_id=existing.id.value)
            validated.append(block)
        self.blocks = sorted(validated, key=lambda b: b.start_at.to_minutes())

    # ── Internal helpers ────────────────────────────────────────

    def _find_block(self, block_id: BlockId) -> DayTemplateBlock:
        for b in self.blocks:
            if b.id == block_id:
                return b
        raise BlockNotFoundError(
            f"Block {block_id.value} not found in day template {self.id.value}"
        )

    def _ensure_no_wraparound(self, block: DayTemplateBlock) -> None:
        if block.end_minutes() > MINUTES_PER_DAY:
            raise InvalidTimeBlockError(
                f"Block {block.id.value} wraps past midnight "
                f"(end at minute {block.end_minutes()})"
            )

    def _ensure_no_overlap(
        self, block: DayTemplateBlock, *, exclude_id: BlockId | None
    ) -> None:
        for existing in self.blocks:
            if exclude_id is not None and existing.id == exclude_id:
                continue
            if existing.overlaps(block):
                raise BlockOverlapError(block_id=existing.id.value)

    def _sort_blocks(self) -> None:
        self.blocks.sort(key=lambda b: b.start_at.to_minutes())

    def _touch(self) -> None:
        self.updated_at = Timestamp.now()
