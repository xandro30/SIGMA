import pytest
import pytest_asyncio
import httpx
from sigma_rest.main import app
from sigma_core.metrics.domain.aggregates.cycle_snapshot import CycleSnapshot
from sigma_core.metrics.domain.aggregates.cycle_summary import CycleSummary
from sigma_core.metrics.domain.value_objects import CardSnapshot, CycleView
from sigma_core.shared_kernel.events import InProcessEventBus
from sigma_rest.dependencies import (
    get_card_reader,
    get_card_repo,
    get_cycle_repo,
    get_cycle_snapshot_repo,
    get_cycle_summary_repo,
    get_day_repo,
    get_day_template_repo,
    get_event_bus,
    get_metrics_card_reader,
    get_metrics_cycle_reader,
    get_metrics_space_reader,
    get_space_reader,
    get_space_repo,
    get_tracking_entry_repo,
    get_week_repo,
    get_week_template_repo,
    get_work_session_repo,
)
from sigma_core.planning.domain.read_models.card_view import CardView
from sigma_core.planning.domain.read_models.space_view import SpaceView
from sigma_core.planning.domain.value_objects import DateRange
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.shared_kernel.value_objects import CardId, SpaceId
from sigma_core.task_management.domain.value_objects import CardTitle, WorkflowStateId
from sigma_core.task_management.domain.enums import PreWorkflowStage
from fakes.fake_card_repository import FakeCardRepository    # type: ignore[import]  # resolved via pytest pythonpath
from fakes.fake_space_repository import FakeSpaceRepository  # type: ignore[import]
from fakes.fake_cycle_repository import FakeCycleRepository  # type: ignore[import]
from fakes.fake_day_repository import FakeDayRepository  # type: ignore[import]
from fakes.fake_day_template_repository import FakeDayTemplateRepository  # type: ignore[import]
from fakes.fake_week_repository import FakeWeekRepository  # type: ignore[import]
from fakes.fake_week_template_repository import FakeWeekTemplateRepository  # type: ignore[import]
from fakes.fake_work_session_repository import FakeWorkSessionRepository  # type: ignore[import]
from fakes.fake_tracking_entry_repository import FakeTrackingEntryRepository  # type: ignore[import]


class _RepoBackedCardReader:
    """Adapter que proyecta un FakeCardRepository a CardView.

    Permite que los tests de integración populen datos vía ``card_repo``
    mientras el router consume el puerto ``CardReader``.
    """

    def __init__(self, repo: FakeCardRepository) -> None:
        self._repo = repo

    async def get_by_id(self, card_id: CardId) -> CardView | None:
        card = await self._repo.get_by_id(card_id)
        if card is None:
            return None
        return _project_card(card)

    async def list_completed_in_range(
        self, space_id: SpaceId, date_range: DateRange
    ) -> list[CardView]:
        cards = await self._repo.get_by_space(space_id)
        result: list[CardView] = []
        for card in cards:
            if card.completed_at is None:
                continue
            if not date_range.contains(card.completed_at.value.date()):
                continue
            result.append(_project_card(card))
        return result


class _RepoBackedSpaceReader:
    def __init__(self, repo: FakeSpaceRepository) -> None:
        self._repo = repo

    async def get_by_id(self, space_id: SpaceId) -> SpaceView | None:
        space = await self._repo.get_by_id(space_id)
        if space is None:
            return None
        return SpaceView(id=space.id, size_mapping=space.size_mapping)


def _project_card(card: Card) -> CardView:
    return CardView(
        id=card.id,
        space_id=card.space_id,
        area_id=card.area_id,
        size=card.size,
        actual_time=card.actual_time,
        completed_at=card.completed_at,
    )


@pytest.fixture
def card_repo():
    return FakeCardRepository()


@pytest.fixture
def space_repo():
    return FakeSpaceRepository()


@pytest.fixture
def cycle_repo():
    return FakeCycleRepository()


@pytest.fixture
def day_repo():
    return FakeDayRepository()


@pytest.fixture
def day_template_repo():
    return FakeDayTemplateRepository()


@pytest.fixture
def week_template_repo():
    return FakeWeekTemplateRepository()


@pytest.fixture
def week_repo():
    return FakeWeekRepository()


@pytest.fixture
def event_bus():
    return InProcessEventBus()


@pytest.fixture
def card_reader(card_repo):
    return _RepoBackedCardReader(card_repo)


@pytest.fixture
def space_reader(space_repo):
    return _RepoBackedSpaceReader(space_repo)


# ── Fakes para metrics BC ───────────────────────────────────────


class _FakeCycleSummaryRepo:
    def __init__(self) -> None:
        self._store: dict[str, CycleSummary] = {}

    async def save(self, summary: CycleSummary) -> None:
        self._store[summary.cycle_id.value] = summary

    async def get_by_cycle_id(self, cycle_id) -> CycleSummary | None:
        return self._store.get(cycle_id.value)


class _FakeCycleSnapshotRepo:
    def __init__(self) -> None:
        self._store: dict[str, CycleSnapshot] = {}

    async def save(self, snapshot: CycleSnapshot) -> None:
        self._store[snapshot.cycle_id.value] = snapshot

    async def get_by_cycle_id(self, cycle_id) -> CycleSnapshot | None:
        return self._store.get(cycle_id.value)


class _RepoBackedMetricsCardReader:
    """Adapta FakeCardRepository a MetricsCardReader con CardSnapshots."""

    def __init__(self, repo) -> None:
        self._repo = repo

    async def list_completed_in_range(self, space_id, date_range):
        cards = await self._repo.get_by_space(space_id)
        result = []
        for card in cards:
            if card.completed_at is None:
                continue
            if not date_range.contains(card.completed_at.value.date()):
                continue
            result.append(
                CardSnapshot(
                    card_id=card.id,
                    area_id=card.area_id,
                    project_id=card.project_id,
                    epic_id=card.epic_id,
                    size=card.size,
                    actual_time_minutes=card.actual_time.value,
                    created_at=card.created_at,
                    entered_workflow_at=card.entered_workflow_at,
                    completed_at=card.completed_at,
                )
            )
        return result


class _RepoBackedMetricsSpaceReader:
    def __init__(self, repo) -> None:
        self._repo = repo

    async def get_size_mapping(self, space_id):
        space = await self._repo.get_by_id(space_id)
        if space is None or space.size_mapping is None:
            return None
        return space.size_mapping.to_primitive()


class _RepoBackedMetricsCycleReader:
    def __init__(self, repo) -> None:
        self._repo = repo

    async def get_by_id(self, cycle_id):
        cycle = await self._repo.get_by_id(cycle_id)
        if cycle is None:
            return None
        return self._to_view(cycle)

    async def get_active_by_space(self, space_id):
        cycle = await self._repo.get_active_by_space(space_id)
        if cycle is None:
            return None
        return self._to_view(cycle)

    @staticmethod
    def _to_view(cycle) -> CycleView:
        return CycleView(
            id=cycle.id,
            space_id=cycle.space_id,
            date_range=cycle.date_range,
            area_budgets={
                aid: m.value for aid, m in cycle.area_budgets.items()
            },
            buffer_percentage=cycle.buffer_percentage,
            state=cycle.state.value,
        )


@pytest.fixture
def work_session_repo():
    return FakeWorkSessionRepository()


@pytest.fixture
def tracking_entry_repo():
    return FakeTrackingEntryRepository()


@pytest.fixture
def cycle_summary_repo():
    return _FakeCycleSummaryRepo()


@pytest.fixture
def cycle_snapshot_repo():
    return _FakeCycleSnapshotRepo()


@pytest.fixture
def metrics_card_reader(card_repo):
    return _RepoBackedMetricsCardReader(card_repo)


@pytest.fixture
def metrics_space_reader(space_repo):
    return _RepoBackedMetricsSpaceReader(space_repo)


@pytest.fixture
def metrics_cycle_reader(cycle_repo):
    return _RepoBackedMetricsCycleReader(cycle_repo)


@pytest_asyncio.fixture
async def client(
    card_repo,
    space_repo,
    cycle_repo,
    day_repo,
    day_template_repo,
    week_template_repo,
    week_repo,
    card_reader,
    space_reader,
    event_bus,
    cycle_summary_repo,
    cycle_snapshot_repo,
    metrics_card_reader,
    metrics_space_reader,
    metrics_cycle_reader,
    work_session_repo,
    tracking_entry_repo,
):
    app.dependency_overrides[get_card_repo]  = lambda: card_repo
    app.dependency_overrides[get_space_repo] = lambda: space_repo
    app.dependency_overrides[get_cycle_repo] = lambda: cycle_repo
    app.dependency_overrides[get_day_repo] = lambda: day_repo
    app.dependency_overrides[get_day_template_repo] = lambda: day_template_repo
    app.dependency_overrides[get_week_template_repo] = lambda: week_template_repo
    app.dependency_overrides[get_week_repo] = lambda: week_repo
    app.dependency_overrides[get_card_reader] = lambda: card_reader
    app.dependency_overrides[get_space_reader] = lambda: space_reader
    app.dependency_overrides[get_event_bus] = lambda: event_bus
    app.dependency_overrides[get_cycle_summary_repo] = lambda: cycle_summary_repo
    app.dependency_overrides[get_cycle_snapshot_repo] = lambda: cycle_snapshot_repo
    app.dependency_overrides[get_metrics_card_reader] = lambda: metrics_card_reader
    app.dependency_overrides[get_metrics_space_reader] = lambda: metrics_space_reader
    app.dependency_overrides[get_metrics_cycle_reader] = lambda: metrics_cycle_reader
    app.dependency_overrides[get_work_session_repo] = lambda: work_session_repo
    app.dependency_overrides[get_tracking_entry_repo] = lambda: tracking_entry_repo
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def card_in_inbox(card_repo):
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Test card in inbox"),
        pre_workflow_stage=PreWorkflowStage.INBOX,
        workflow_state_id=None,
    )
    await card_repo.save(card)
    return card


@pytest_asyncio.fixture
async def card_in_refinement(card_repo):
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Test card in refinement"),
        pre_workflow_stage=PreWorkflowStage.REFINEMENT,
        workflow_state_id=None,
    )
    await card_repo.save(card)
    return card


@pytest_asyncio.fixture
async def card_in_workflow(card_repo):
    card = Card(
        id=CardId.generate(),
        space_id=SpaceId.generate(),
        title=CardTitle("Test card in workflow"),
        pre_workflow_stage=None,
        workflow_state_id=WorkflowStateId.generate(),
    )
    await card_repo.save(card)
    return card
