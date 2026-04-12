from dataclasses import dataclass

from sigma_core.planning.domain.aggregates.week import Week
from sigma_core.planning.domain.errors import WeekNotFoundError
from sigma_core.planning.domain.ports.week_repository import WeekRepository
from sigma_core.planning.domain.value_objects import WeekId


@dataclass
class GetWeekQuery:
    week_id: WeekId


class GetWeek:
    """Recupera un ``Week`` por su id.

    Lanza ``WeekNotFoundError`` si no existe — el adaptador HTTP lo mapea
    a 404. Esta es la puerta de entrada habitual para que el UI pinte la
    semana (notas, template aplicado) junto con los days consultados en
    paralelo.
    """

    def __init__(self, week_repo: WeekRepository) -> None:
        self._week_repo = week_repo

    async def execute(self, query: GetWeekQuery) -> Week:
        week = await self._week_repo.get_by_id(query.week_id)
        if week is None:
            raise WeekNotFoundError(f"Week {query.week_id.value} not found")
        return week
