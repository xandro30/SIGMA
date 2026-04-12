from dataclasses import dataclass
from datetime import date

from sigma_core.planning.domain.aggregates.day import Day
from sigma_core.planning.domain.ports.day_repository import DayRepository
from sigma_core.planning.domain.value_objects import DayId
from sigma_core.shared_kernel.value_objects import SpaceId


@dataclass
class CreateDayCommand:
    space_id: SpaceId
    target_date: date


class CreateDay:
    """Crea un `Day` vacío para `(space_id, target_date)` si no existe.

    Idempotente y race-safe: el DayId se deriva de forma determinista de
    ``(space_id, target_date)``, de modo que dos requests concurrentes
    calculan la misma ID y Firestore deduplica al escribir en el mismo
    documento. No hay riesgo de duplicar el día.
    """

    def __init__(self, day_repo: DayRepository) -> None:
        self._day_repo = day_repo

    async def execute(self, cmd: CreateDayCommand) -> DayId:
        day_id = DayId.for_space_and_date(cmd.space_id, cmd.target_date)
        existing = await self._day_repo.get_by_id(day_id)
        if existing is not None:
            return existing.id

        day = Day(
            id=day_id,
            space_id=cmd.space_id,
            date=cmd.target_date,
        )
        await self._day_repo.save(day)
        return day.id
