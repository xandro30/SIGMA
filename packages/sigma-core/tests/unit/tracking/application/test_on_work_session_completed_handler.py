"""Unit tests para OnWorkSessionCompletedHandler."""
import pytest
from datetime import datetime
from zoneinfo import ZoneInfo

from sigma_core.shared_kernel.events import WorkSessionCompleted
from sigma_core.shared_kernel.value_objects import CardId, SpaceId, Timestamp
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import BEGIN_STATE_ID
from sigma_core.task_management.domain.value_objects import CardTitle
from sigma_core.tracking.application.event_handlers.on_work_session_completed import (
    OnWorkSessionCompletedHandler,
)
from tests.fakes.fake_card_repository import FakeCardRepository

MADRID = ZoneInfo("Europe/Madrid")


def _ts(offset_minutes: int = 0) -> Timestamp:
    base = datetime(2026, 4, 14, 9, 0, tzinfo=MADRID)
    from datetime import timedelta
    return Timestamp(base + timedelta(minutes=offset_minutes))


def _make_card(card_id: CardId, space_id: SpaceId) -> Card:
    return Card(
        id=card_id,
        space_id=space_id,
        title=CardTitle("Test card"),
        pre_workflow_stage=None,
        workflow_state_id=BEGIN_STATE_ID,
    )


def _make_event(card_id: CardId, space_id: SpaceId, minutes: int = 25) -> WorkSessionCompleted:
    return WorkSessionCompleted(
        occurred_at=_ts(25),
        space_id=space_id,
        card_id=card_id,
        area_id=None,
        project_id=None,
        epic_id=None,
        description="Test session",
        minutes=minutes,
    )


class TestOnWorkSessionCompletedHandler:
    def _setup(self):
        self.card_repo = FakeCardRepository()
        self.handler = OnWorkSessionCompletedHandler(self.card_repo)

    @pytest.mark.asyncio
    async def test_handler_adds_work_log_entry(self):
        self._setup()
        card_id = CardId.generate()
        space_id = SpaceId.generate()
        card = _make_card(card_id, space_id)
        await self.card_repo.save(card)

        event = _make_event(card_id, space_id, minutes=25)
        await self.handler(event)

        updated = await self.card_repo.get_by_id(card_id)
        assert updated is not None
        assert len(updated.work_log) == 1
        assert updated.work_log[0].minutes == 25
        assert updated.work_log[0].log == "Test session"

    @pytest.mark.asyncio
    async def test_handler_accumulates_actual_time(self):
        self._setup()
        card_id = CardId.generate()
        space_id = SpaceId.generate()
        card = _make_card(card_id, space_id)
        await self.card_repo.save(card)

        await self.handler(_make_event(card_id, space_id, minutes=25))
        await self.handler(_make_event(card_id, space_id, minutes=30))

        updated = await self.card_repo.get_by_id(card_id)
        assert updated is not None
        assert len(updated.work_log) == 2
        assert updated.actual_time.value == 55

    @pytest.mark.asyncio
    async def test_handler_skips_if_card_not_found(self):
        """Si la card no existe, el handler no falla — simplemente no hace nada."""
        self._setup()
        event = _make_event(CardId.generate(), SpaceId.generate(), minutes=25)
        # No debe lanzar excepción
        await self.handler(event)
