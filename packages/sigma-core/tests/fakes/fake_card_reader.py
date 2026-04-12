from sigma_core.planning.domain.read_models.card_view import CardView
from sigma_core.planning.domain.value_objects import DateRange
from sigma_core.shared_kernel.value_objects import CardId, SpaceId


class FakeCardReader:
    """In-memory fake for the planning.CardReader port."""

    def __init__(self) -> None:
        self._cards: list[CardView] = []

    def add(self, card: CardView) -> None:
        self._cards.append(card)

    async def get_by_id(self, card_id: CardId) -> CardView | None:
        for c in self._cards:
            if c.id == card_id:
                return c
        return None

    async def list_completed_in_range(
        self, space_id: SpaceId, date_range: DateRange
    ) -> list[CardView]:
        return [
            c
            for c in self._cards
            if c.space_id == space_id
            and c.completed_at is not None
            and date_range.contains(c.completed_at.value.date())
        ]
