from __future__ import annotations

from typing import Protocol

from sigma_core.planning.domain.read_models.card_view import CardView
from sigma_core.planning.domain.value_objects import DateRange
from sigma_core.shared_kernel.value_objects import CardId, SpaceId


class CardReader(Protocol):
    """Port for reading Card projections from within the planning BC.

    Only exposes the operations planning queries need. The concrete
    implementation lives in `planning.infrastructure` and is responsible
    for mapping persistence data (shared with task_management) to
    `CardView` DTOs — planning.domain/application never touches the
    task_management Card aggregate.
    """

    async def get_by_id(self, card_id: CardId) -> CardView | None:
        ...

    async def list_completed_in_range(
        self, space_id: SpaceId, date_range: DateRange
    ) -> list[CardView]:
        """Cards from `space_id` whose `completed_at` falls inside `date_range`.

        Cards with `completed_at is None` are excluded.
        """
        ...
