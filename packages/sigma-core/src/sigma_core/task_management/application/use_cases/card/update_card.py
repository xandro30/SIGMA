from dataclasses import dataclass, field
from datetime import date
from sigma_core.task_management.domain.enums import Priority
from sigma_core.task_management.domain.errors import (
    CardNotFoundError, AreaNotFoundError, EpicNotFoundError, InvalidEpicSpaceError,
)
from sigma_core.task_management.domain.value_objects import (
    CardId, CardTitle, AreaId, EpicId,
)
from sigma_core.task_management.domain.ports.card_repository import CardRepository
from sigma_core.task_management.domain.ports.area_repository import AreaRepository
from sigma_core.task_management.domain.ports.epic_repository import EpicRepository


# Sentinel: distingue "campo no enviado" de "null = limpiar asignación"
class _Unset:
    _instance: "_Unset | None" = None

    def __new__(cls) -> "_Unset":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "UNSET"


UNSET = _Unset()


@dataclass
class UpdateCardCommand:
    card_id: CardId
    title: CardTitle | None = None
    description: str | None = None
    priority: Priority | None = None
    due_date: date | None = None
    # UNSET = no tocar; None = limpiar asignación; AreaId/EpicId = asignar
    area_id: AreaId | None | _Unset = field(default_factory=lambda: UNSET)
    epic_id: EpicId | None | _Unset = field(default_factory=lambda: UNSET)
    # None = no tocar; set vacío = limpiar; set con valores = reemplazar
    labels: set[str] | None = None


class UpdateCard:
    def __init__(
        self,
        card_repo: CardRepository,
        area_repo: AreaRepository,
        epic_repo: EpicRepository,
    ) -> None:
        self._card_repo = card_repo
        self._area_repo = area_repo
        self._epic_repo = epic_repo

    async def execute(self, cmd: UpdateCardCommand) -> None:
        card = await self._card_repo.get_by_id(cmd.card_id)
        if card is None:
            raise CardNotFoundError(cmd.card_id)

        if cmd.title is not None:
            card.title = cmd.title
        if cmd.description is not None:
            card.description = cmd.description
        if cmd.priority is not None:
            card.priority = cmd.priority
        if cmd.due_date is not None:
            card.due_date = cmd.due_date

        if not isinstance(cmd.area_id, _Unset):
            if cmd.area_id is not None:
                area = await self._area_repo.get_by_id(cmd.area_id)
                if area is None:
                    raise AreaNotFoundError(cmd.area_id)
            card.area_id = cmd.area_id

        if not isinstance(cmd.epic_id, _Unset):
            if cmd.epic_id is not None:
                epic = await self._epic_repo.get_by_id(cmd.epic_id)
                if epic is None:
                    raise EpicNotFoundError(cmd.epic_id)
                if epic.space_id != card.space_id:
                    raise InvalidEpicSpaceError("Epic belongs to a different Space")
            card.epic_id = cmd.epic_id

        if cmd.labels is not None:
            card.labels = cmd.labels

        await self._card_repo.save(card)
