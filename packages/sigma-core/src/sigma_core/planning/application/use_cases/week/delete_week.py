from dataclasses import dataclass
from datetime import timedelta

from sigma_core.planning.domain.errors import WeekNotFoundError
from sigma_core.planning.domain.ports.day_repository import DayRepository
from sigma_core.planning.domain.ports.week_repository import WeekRepository
from sigma_core.planning.domain.value_objects import DayId, WeekId


@dataclass
class DeleteWeekCommand:
    week_id: WeekId


class DeleteWeek:
    """Elimina un ``Week`` y sus 7 ``Day`` materializados en cascada.

    La cascada borra por id determinista: ``DayId.for_space_and_date`` para
    cada uno de los 7 días del rango. Los ``Day`` que no estaban
    materializados no existen y el repo los trata como no-op.

    Este use case asume que la política de cascada es SIEMPRE activa: si el
    usuario borra la semana, los Days dentro del rango son propiedad lógica
    de la semana y deben desaparecer con ella. Para borrar el ``Week`` sin
    tocar los Days, el flujo sería otro (aún no hay caso de uso).
    """

    def __init__(
        self,
        week_repo: WeekRepository,
        day_repo: DayRepository,
    ) -> None:
        self._week_repo = week_repo
        self._day_repo = day_repo

    async def execute(self, cmd: DeleteWeekCommand) -> None:
        week = await self._week_repo.get_by_id(cmd.week_id)
        if week is None:
            raise WeekNotFoundError(f"Week {cmd.week_id.value} not found")

        for offset in range(7):
            target_date = week.week_start + timedelta(days=offset)
            day_id = DayId.for_space_and_date(week.space_id, target_date)
            await self._day_repo.delete(day_id)

        await self._week_repo.delete(cmd.week_id)
