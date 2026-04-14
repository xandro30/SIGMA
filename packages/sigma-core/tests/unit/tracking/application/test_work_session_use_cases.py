"""Unit tests para use cases del tracking BC."""
import pytest
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sigma_core.shared_kernel.events import InProcessEventBus, WorkSessionCompleted
from sigma_core.shared_kernel.value_objects import CardId, SpaceId, Timestamp
from sigma_core.tracking.domain.aggregates.work_session import WorkSessionState
from sigma_core.tracking.domain.errors import (
    WorkSessionAlreadyActiveError,
    WorkSessionNotFoundError,
)
from sigma_core.tracking.domain.value_objects.timer import Timer, TimerTechnique
from sigma_core.tracking.application.use_cases.start_work_session import (
    StartWorkSession, StartWorkSessionCommand,
)
from sigma_core.tracking.application.use_cases.complete_round import CompleteRound
from sigma_core.tracking.application.use_cases.resume_from_break import ResumeFromBreak
from sigma_core.tracking.application.use_cases.stop_work_session import (
    StopWorkSession, StopWorkSessionCommand,
)
from sigma_core.tracking.application.use_cases.get_active_session import GetActiveSession
from tests.fakes.fake_work_session_repository import FakeWorkSessionRepository
from tests.fakes.fake_tracking_entry_repository import FakeTrackingEntryRepository
MADRID = ZoneInfo("Europe/Madrid")


def _ts(offset: int = 0) -> Timestamp:
    base = datetime(2026, 4, 14, 9, 0, tzinfo=MADRID)
    return Timestamp(base + timedelta(minutes=offset))


def _timer(rounds: int = 4) -> Timer:
    return Timer(technique=TimerTechnique.POMODORO, work_minutes=25, break_minutes=5, num_rounds=rounds)


# ── StartWorkSession ──────────────────────────────────────────────

class TestStartWorkSession:
    def _uc(self):
        self.session_repo = FakeWorkSessionRepository()
        return StartWorkSession(self.session_repo)

    @pytest.mark.asyncio
    async def test_start_creates_session_in_working_state(self):
        uc = self._uc()
        card_id = CardId.generate()
        space_id = SpaceId.generate()
        cmd = StartWorkSessionCommand(
            space_id=space_id, card_id=card_id, area_id=None,
            project_id=None, epic_id=None, description="Test",
            timer=_timer(), now=_ts(),
        )
        session = await uc.execute(cmd)
        assert session.state == WorkSessionState.WORKING
        assert session.space_id == space_id
        assert session.card_id == card_id

    @pytest.mark.asyncio
    async def test_start_persists_session(self):
        uc = self._uc()
        cmd = StartWorkSessionCommand(
            space_id=SpaceId.generate(), card_id=CardId.generate(),
            area_id=None, project_id=None, epic_id=None,
            description="Test", timer=_timer(), now=_ts(),
        )
        session = await uc.execute(cmd)
        saved = await self.session_repo.get_by_space(session.space_id)
        assert saved is not None
        assert saved.id == session.id

    @pytest.mark.asyncio
    async def test_start_with_existing_active_session_raises(self):
        uc = self._uc()
        space_id = SpaceId.generate()
        cmd = StartWorkSessionCommand(
            space_id=space_id, card_id=CardId.generate(),
            area_id=None, project_id=None, epic_id=None,
            description="First", timer=_timer(), now=_ts(),
        )
        await uc.execute(cmd)
        with pytest.raises(WorkSessionAlreadyActiveError):
            await uc.execute(StartWorkSessionCommand(
                space_id=space_id, card_id=CardId.generate(),
                area_id=None, project_id=None, epic_id=None,
                description="Second", timer=_timer(), now=_ts(5),
            ))


# ── CompleteRound ─────────────────────────────────────────────────

class TestCompleteRound:
    def _setup(self, rounds: int = 4):
        self.session_repo = FakeWorkSessionRepository()
        self.bus = InProcessEventBus()
        self.uc_start = StartWorkSession(self.session_repo)
        self.uc = CompleteRound(self.session_repo, self.bus)

    async def _start(self, space_id=None, rounds=4):
        space_id = space_id or SpaceId.generate()
        cmd = StartWorkSessionCommand(
            space_id=space_id, card_id=CardId.generate(),
            area_id=None, project_id=None, epic_id=None,
            description="Test", timer=_timer(rounds), now=_ts(),
        )
        return await self.uc_start.execute(cmd)

    @pytest.mark.asyncio
    async def test_complete_round_increments_counter(self):
        self._setup()
        session = await self._start()
        updated = await self.uc.execute(session.space_id, _ts(25))
        assert updated.completed_rounds == 1

    @pytest.mark.asyncio
    async def test_complete_round_transitions_to_break(self):
        self._setup()
        session = await self._start(rounds=4)
        updated = await self.uc.execute(session.space_id, _ts(25))
        assert updated.state == WorkSessionState.BREAK

    @pytest.mark.asyncio
    async def test_complete_last_round_publishes_event(self):
        self._setup()
        received = []

        async def _on_event(e): received.append(e)

        self.bus.subscribe(WorkSessionCompleted, _on_event)
        session = await self._start(rounds=1)
        await self.uc.execute(session.space_id, _ts(25))
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_complete_round_session_not_found_raises(self):
        self._setup()
        with pytest.raises(WorkSessionNotFoundError):
            await self.uc.execute(SpaceId.generate(), _ts(25))


# ── ResumeFromBreak ───────────────────────────────────────────────

class TestResumeFromBreak:
    def _setup(self):
        self.session_repo = FakeWorkSessionRepository()
        self.uc_start = StartWorkSession(self.session_repo)
        self.uc_round = CompleteRound(self.session_repo, InProcessEventBus())
        self.uc = ResumeFromBreak(self.session_repo)

    @pytest.mark.asyncio
    async def test_resume_transitions_to_working(self):
        self._setup()
        cmd = StartWorkSessionCommand(
            space_id=SpaceId.generate(), card_id=CardId.generate(),
            area_id=None, project_id=None, epic_id=None,
            description="Test", timer=_timer(4), now=_ts(),
        )
        session = await self.uc_start.execute(cmd)
        await self.uc_round.execute(session.space_id, _ts(25))  # → BREAK
        updated = await self.uc.execute(session.space_id, _ts(30))
        assert updated.state == WorkSessionState.WORKING

    @pytest.mark.asyncio
    async def test_resume_not_found_raises(self):
        self._setup()
        with pytest.raises(WorkSessionNotFoundError):
            await self.uc.execute(SpaceId.generate(), _ts(30))


# ── StopWorkSession ───────────────────────────────────────────────

class TestStopWorkSession:
    def _setup(self):
        self.session_repo = FakeWorkSessionRepository()
        self.entry_repo = FakeTrackingEntryRepository()
        self.bus = InProcessEventBus()
        self.uc_start = StartWorkSession(self.session_repo)
        self.uc = StopWorkSession(self.session_repo, self.entry_repo, self.bus)

    async def _start(self, space_id=None) -> SpaceId:
        space_id = space_id or SpaceId.generate()
        cmd = StartWorkSessionCommand(
            space_id=space_id, card_id=CardId.generate(),
            area_id=None, project_id=None, epic_id=None,
            description="Test", timer=_timer(), now=_ts(),
        )
        await self.uc_start.execute(cmd)
        return space_id

    @pytest.mark.asyncio
    async def test_stop_with_save_creates_tracking_entry(self):
        self._setup()
        space_id = await self._start()
        cmd = StopWorkSessionCommand(space_id=space_id, save=True, now=_ts(18))
        await self.uc.execute(cmd)
        entries = await self.entry_repo.list_by_space(space_id)
        assert len(entries) == 1
        assert entries[0].minutes == 18

    @pytest.mark.asyncio
    async def test_stop_with_save_publishes_event(self):
        self._setup()
        received = []

        async def _on_event(e): received.append(e)

        self.bus.subscribe(WorkSessionCompleted, _on_event)
        space_id = await self._start()
        await self.uc.execute(StopWorkSessionCommand(space_id=space_id, save=True, now=_ts(18)))
        assert len(received) == 1

    @pytest.mark.asyncio
    async def test_stop_with_save_deletes_session(self):
        self._setup()
        space_id = await self._start()
        await self.uc.execute(StopWorkSessionCommand(space_id=space_id, save=True, now=_ts(18)))
        assert await self.session_repo.get_by_space(space_id) is None

    @pytest.mark.asyncio
    async def test_stop_discard_no_tracking_entry(self):
        self._setup()
        space_id = await self._start()
        await self.uc.execute(StopWorkSessionCommand(space_id=space_id, save=False, now=_ts(18)))
        entries = await self.entry_repo.list_by_space(space_id)
        assert entries == []

    @pytest.mark.asyncio
    async def test_stop_discard_no_event_published(self):
        self._setup()
        received = []

        async def _on_event(e): received.append(e)

        self.bus.subscribe(WorkSessionCompleted, _on_event)
        space_id = await self._start()
        await self.uc.execute(StopWorkSessionCommand(space_id=space_id, save=False, now=_ts(18)))
        assert received == []

    @pytest.mark.asyncio
    async def test_stop_not_found_raises(self):
        self._setup()
        with pytest.raises(WorkSessionNotFoundError):
            await self.uc.execute(StopWorkSessionCommand(space_id=SpaceId.generate(), save=True, now=_ts()))


# ── GetActiveSession ──────────────────────────────────────────────

class TestGetActiveSession:
    @pytest.mark.asyncio
    async def test_get_returns_active_session(self):
        repo = FakeWorkSessionRepository()
        uc_start = StartWorkSession(repo)
        uc_get = GetActiveSession(repo)
        space_id = SpaceId.generate()
        cmd = StartWorkSessionCommand(
            space_id=space_id, card_id=CardId.generate(),
            area_id=None, project_id=None, epic_id=None,
            description="Test", timer=_timer(), now=_ts(),
        )
        started = await uc_start.execute(cmd)
        found = await uc_get.execute(space_id)
        assert found is not None
        assert found.id == started.id

    @pytest.mark.asyncio
    async def test_get_returns_none_when_no_session(self):
        repo = FakeWorkSessionRepository()
        uc = GetActiveSession(repo)
        result = await uc.execute(SpaceId.generate())
        assert result is None

