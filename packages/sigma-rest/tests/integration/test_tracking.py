"""Integration tests para el router de tracking."""
import pytest
import pytest_asyncio
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import BEGIN_STATE_ID
from sigma_core.task_management.domain.value_objects import CardTitle
from sigma_core.shared_kernel.value_objects import CardId, SpaceId


def _make_card(space_id: SpaceId) -> Card:
    return Card(
        id=CardId.generate(),
        space_id=space_id,
        title=CardTitle("Test card"),
        pre_workflow_stage=None,
        workflow_state_id=BEGIN_STATE_ID,
    )


def _session_body(card_id: str) -> dict:
    return {
        "card_id": card_id,
        "description": "Test session",
        "timer": {
            "technique": "pomodoro",
            "work_minutes": 25,
            "break_minutes": 5,
            "num_rounds": 4,
        },
    }


class TestStartWorkSession:
    @pytest_asyncio.fixture
    async def space_with_card(self, card_repo):
        space_id = SpaceId.generate()
        card = _make_card(space_id)
        await card_repo.save(card)
        return space_id, card

    @pytest.mark.asyncio
    async def test_start_returns_201(self, client, space_with_card):
        space_id, card = space_with_card
        resp = await client.post(
            f"/v1/spaces/{space_id.value}/tracking/sessions",
            json=_session_body(card.id.value),
        )
        assert resp.status_code == 201

    @pytest.mark.asyncio
    async def test_start_response_body(self, client, space_with_card):
        space_id, card = space_with_card
        resp = await client.post(
            f"/v1/spaces/{space_id.value}/tracking/sessions",
            json=_session_body(card.id.value),
        )
        data = resp.json()
        assert data["state"] == "working"
        assert data["space_id"] == space_id.value
        assert data["card_id"] == card.id.value
        assert data["completed_rounds"] == 0

    @pytest.mark.asyncio
    async def test_start_duplicate_raises_conflict(self, client, space_with_card):
        space_id, card = space_with_card
        body = _session_body(card.id.value)
        await client.post(f"/v1/spaces/{space_id.value}/tracking/sessions", json=body)
        resp = await client.post(
            f"/v1/spaces/{space_id.value}/tracking/sessions", json=body
        )
        assert resp.status_code == 409


class TestGetActiveSession:
    @pytest.mark.asyncio
    async def test_get_no_session_returns_204(self, client):
        space_id = SpaceId.generate()
        resp = await client.get(f"/v1/spaces/{space_id.value}/tracking/sessions/active")
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_get_active_session_returns_200(self, client, card_repo):
        space_id = SpaceId.generate()
        card = _make_card(space_id)
        await card_repo.save(card)
        await client.post(
            f"/v1/spaces/{space_id.value}/tracking/sessions",
            json=_session_body(card.id.value),
        )
        resp = await client.get(f"/v1/spaces/{space_id.value}/tracking/sessions/active")
        assert resp.status_code == 200
        assert resp.json()["state"] == "working"


class TestCompleteRound:
    @pytest.mark.asyncio
    async def test_complete_round_transitions_to_break(self, client, card_repo):
        space_id = SpaceId.generate()
        card = _make_card(space_id)
        await card_repo.save(card)
        await client.post(
            f"/v1/spaces/{space_id.value}/tracking/sessions",
            json=_session_body(card.id.value),
        )
        resp = await client.post(
            f"/v1/spaces/{space_id.value}/tracking/sessions/rounds"
        )
        assert resp.status_code == 200
        assert resp.json()["state"] == "break"
        assert resp.json()["completed_rounds"] == 1

    @pytest.mark.asyncio
    async def test_complete_round_not_found_raises(self, client):
        space_id = SpaceId.generate()
        resp = await client.post(
            f"/v1/spaces/{space_id.value}/tracking/sessions/rounds"
        )
        assert resp.status_code == 404


class TestResumeFromBreak:
    @pytest.mark.asyncio
    async def test_resume_transitions_to_working(self, client, card_repo):
        space_id = SpaceId.generate()
        card = _make_card(space_id)
        await card_repo.save(card)
        await client.post(
            f"/v1/spaces/{space_id.value}/tracking/sessions",
            json=_session_body(card.id.value),
        )
        # complete a round → BREAK
        await client.post(f"/v1/spaces/{space_id.value}/tracking/sessions/rounds")
        resp = await client.post(
            f"/v1/spaces/{space_id.value}/tracking/sessions/resume"
        )
        assert resp.status_code == 200
        assert resp.json()["state"] == "working"


class TestStopWorkSession:
    @pytest.mark.asyncio
    async def test_stop_with_save_returns_204(self, client, card_repo):
        space_id = SpaceId.generate()
        card = _make_card(space_id)
        await card_repo.save(card)
        await client.post(
            f"/v1/spaces/{space_id.value}/tracking/sessions",
            json=_session_body(card.id.value),
        )
        resp = await client.delete(
            f"/v1/spaces/{space_id.value}/tracking/sessions?save=true"
        )
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_stop_discard_returns_204(self, client, card_repo):
        space_id = SpaceId.generate()
        card = _make_card(space_id)
        await card_repo.save(card)
        await client.post(
            f"/v1/spaces/{space_id.value}/tracking/sessions",
            json=_session_body(card.id.value),
        )
        resp = await client.delete(
            f"/v1/spaces/{space_id.value}/tracking/sessions?save=false"
        )
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_stop_not_found_raises(self, client):
        space_id = SpaceId.generate()
        resp = await client.delete(
            f"/v1/spaces/{space_id.value}/tracking/sessions?save=true"
        )
        assert resp.status_code == 404
