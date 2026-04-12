from dataclasses import dataclass
from datetime import date

from sigma_core.planning.domain.aggregates.week import Week
from sigma_core.planning.domain.ports.week_repository import WeekRepository
from sigma_core.planning.domain.value_objects import WeekId
from sigma_core.shared_kernel.value_objects import SpaceId


@dataclass
class CreateWeekCommand:
    space_id: SpaceId
    week_start: date


class CreateWeek:
    """Crea un ``Week`` vacío para ``(space_id, week_start)`` si no existe.

    Idempotente y race-safe por la misma razón que ``CreateDay``: el
    ``WeekId`` es determinista, de modo que dos requests concurrentes
    escriben el mismo documento Firestore y el segundo sobrescribe sin
    duplicar.

    No materializa los 7 ``Day``: esa es responsabilidad de
    ``ApplyTemplateToWeek`` o del propio ``CreateDay`` individual.
    """

    def __init__(self, week_repo: WeekRepository) -> None:
        self._week_repo = week_repo

    async def execute(self, cmd: CreateWeekCommand) -> WeekId:
        week_id = WeekId.for_space_and_week_start(cmd.space_id, cmd.week_start)
        existing = await self._week_repo.get_by_id(week_id)
        if existing is not None:
            return existing.id

        week = Week(
            id=week_id,
            space_id=cmd.space_id,
            week_start=cmd.week_start,
        )
        await self._week_repo.save(week)
        return week.id
