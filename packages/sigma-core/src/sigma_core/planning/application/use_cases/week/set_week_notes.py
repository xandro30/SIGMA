from dataclasses import dataclass

from sigma_core.planning.domain.errors import WeekNotFoundError
from sigma_core.planning.domain.ports.week_repository import WeekRepository
from sigma_core.planning.domain.value_objects import WeekId


@dataclass
class SetWeekNotesCommand:
    week_id: WeekId
    notes: str


class SetWeekNotes:
    """Actualiza las notas libres de un ``Week``.

    El caso de uso recupera el agregado, delega la mutación al agregado
    (que valida y bumpea ``updated_at``) y persiste.
    """

    def __init__(self, week_repo: WeekRepository) -> None:
        self._week_repo = week_repo

    async def execute(self, cmd: SetWeekNotesCommand) -> None:
        week = await self._week_repo.get_by_id(cmd.week_id)
        if week is None:
            raise WeekNotFoundError(f"Week {cmd.week_id.value} not found")
        week.set_notes(cmd.notes)
        await self._week_repo.save(week)
