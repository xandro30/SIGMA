"""
Integration tests for the 4 card movement types:

  Preworkflow → Preworkflow : PATCH /cards/{id}/triage-stage  (covered in test_cards_triage.py)
  Preworkflow → Workflow    : PATCH /cards/{id}/promote
  Workflow    → Workflow    : PATCH /cards/{id}/move
  Workflow    → Preworkflow : PATCH /cards/{id}/demote
"""
import pytest
import pytest_asyncio
from sigma_core.task_management.domain.aggregates.card import Card
from sigma_core.task_management.domain.aggregates.space import (
    Space, WorkflowState, BEGIN_STATE_ID, FINISH_STATE_ID,
)
from sigma_core.shared_kernel.value_objects import CardId, SpaceId
from sigma_core.task_management.domain.value_objects import (
    SpaceName,
    CardTitle,
    WorkflowStateId,
)
from sigma_core.task_management.domain.enums import PreWorkflowStage


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_space_with_one_state():
    """Space with BEGIN → In Progress → FINISH transitions."""
    space = Space(id=SpaceId.generate(), name=SpaceName("Test Space"))
    state_id = WorkflowStateId.generate()
    state = WorkflowState(id=state_id, name="In Progress", order=1)
    space.add_state(state)
    space.add_transition(BEGIN_STATE_ID, state_id)
    space.add_transition(state_id, FINISH_STATE_ID)
    return space, state_id


# ── promote_card : Preworkflow → Workflow ─────────────────────────────────────

class TestPromoteCard:

    @pytest_asyncio.fixture
    async def backlog_card_with_space(self, card_repo, space_repo):
        space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
        card = Card(
            id=CardId.generate(),
            space_id=space.id,
            title=CardTitle("Card lista para workflow"),
            pre_workflow_stage=PreWorkflowStage.BACKLOG,
            workflow_state_id=None,
        )
        await space_repo.save(space)
        await card_repo.save(card)
        return card, space

    @pytest_asyncio.fixture
    async def inbox_card_with_space(self, card_repo, space_repo):
        space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
        card = Card(
            id=CardId.generate(),
            space_id=space.id,
            title=CardTitle("Card en inbox"),
            pre_workflow_stage=PreWorkflowStage.INBOX,
            workflow_state_id=None,
        )
        await space_repo.save(space)
        await card_repo.save(card)
        return card, space

    async def test_promote_backlog_card_defaults_to_begin(self, client, backlog_card_with_space):
        card, _ = backlog_card_with_space
        response = await client.patch(
            f"/v1/cards/{card.id.value}/promote",
            json={"target_state_id": None},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["workflow_state_id"] == BEGIN_STATE_ID.value
        assert body["pre_workflow_stage"] is None

    async def test_promote_inbox_card_to_begin(self, client, inbox_card_with_space):
        card, _ = inbox_card_with_space
        response = await client.patch(
            f"/v1/cards/{card.id.value}/promote",
            json={"target_state_id": None},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["workflow_state_id"] == BEGIN_STATE_ID.value
        assert body["pre_workflow_stage"] is None

    async def test_promote_to_specific_state(self, client, card_repo, space_repo):
        space, state_id = _make_space_with_one_state()
        card = Card(
            id=CardId.generate(),
            space_id=space.id,
            title=CardTitle("Card para promover"),
            pre_workflow_stage=PreWorkflowStage.BACKLOG,
            workflow_state_id=None,
        )
        await space_repo.save(space)
        await card_repo.save(card)

        response = await client.patch(
            f"/v1/cards/{card.id.value}/promote",
            json={"target_state_id": state_id.value},
        )

        assert response.status_code == 200
        assert response.json()["workflow_state_id"] == state_id.value

    async def test_promote_card_already_in_workflow_returns_422(self, client, card_repo, space_repo):
        space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
        card = Card(
            id=CardId.generate(),
            space_id=space.id,
            title=CardTitle("Card en workflow"),
            pre_workflow_stage=None,
            workflow_state_id=BEGIN_STATE_ID,
        )
        await space_repo.save(space)
        await card_repo.save(card)

        response = await client.patch(
            f"/v1/cards/{card.id.value}/promote",
            json={"target_state_id": None},
        )

        assert response.status_code == 422

    async def test_promote_card_not_found_returns_404(self, client):
        response = await client.patch(
            f"/v1/cards/{CardId.generate().value}/promote",
            json={"target_state_id": None},
        )

        assert response.status_code == 404
        assert response.json()["error"] == "card_not_found"


# ── move_card : Workflow → Workflow ───────────────────────────────────────────

class TestMoveCard:

    @pytest_asyncio.fixture
    async def card_at_begin(self, card_repo, space_repo):
        space, in_progress_id = _make_space_with_one_state()
        card = Card(
            id=CardId.generate(),
            space_id=space.id,
            title=CardTitle("Card en BEGIN"),
            pre_workflow_stage=None,
            workflow_state_id=BEGIN_STATE_ID,
        )
        await space_repo.save(space)
        await card_repo.save(card)
        return card, space, in_progress_id

    async def test_move_card_to_valid_next_state(self, client, card_at_begin):
        card, _, in_progress_id = card_at_begin
        response = await client.patch(
            f"/v1/cards/{card.id.value}/move",
            json={"target_state_id": in_progress_id.value},
        )

        assert response.status_code == 200
        assert response.json()["workflow_state_id"] == in_progress_id.value
        assert response.json()["pre_workflow_stage"] is None

    async def test_move_card_to_finish(self, client, card_repo, space_repo):
        space, in_progress_id = _make_space_with_one_state()
        card = Card(
            id=CardId.generate(),
            space_id=space.id,
            title=CardTitle("Card en In Progress"),
            pre_workflow_stage=None,
            workflow_state_id=in_progress_id,
        )
        await space_repo.save(space)
        await card_repo.save(card)

        response = await client.patch(
            f"/v1/cards/{card.id.value}/move",
            json={"target_state_id": FINISH_STATE_ID.value},
        )

        assert response.status_code == 200
        assert response.json()["workflow_state_id"] == FINISH_STATE_ID.value

    async def test_move_card_invalid_transition_returns_422(self, client, card_at_begin):
        card, _, _ = card_at_begin
        response = await client.patch(
            f"/v1/cards/{card.id.value}/move",
            json={"target_state_id": FINISH_STATE_ID.value},
        )

        assert response.status_code == 422

    async def test_move_card_in_preworkflow_returns_422(self, client, card_repo, space_repo):
        space = Space(id=SpaceId.generate(), name=SpaceName("Work"))
        card = Card(
            id=CardId.generate(),
            space_id=space.id,
            title=CardTitle("Card en backlog"),
            pre_workflow_stage=PreWorkflowStage.BACKLOG,
            workflow_state_id=None,
        )
        await space_repo.save(space)
        await card_repo.save(card)

        response = await client.patch(
            f"/v1/cards/{card.id.value}/move",
            json={"target_state_id": BEGIN_STATE_ID.value},
        )

        assert response.status_code == 422

    async def test_move_card_not_found_returns_404(self, client):
        response = await client.patch(
            f"/v1/cards/{CardId.generate().value}/move",
            json={"target_state_id": BEGIN_STATE_ID.value},
        )

        assert response.status_code == 404
        assert response.json()["error"] == "card_not_found"


# ── demote_card : Workflow → Preworkflow ──────────────────────────────────────

class TestDemoteCard:

    @pytest_asyncio.fixture
    async def workflow_card(self, card_repo):
        card = Card(
            id=CardId.generate(),
            space_id=SpaceId.generate(),
            title=CardTitle("Card en workflow"),
            pre_workflow_stage=None,
            workflow_state_id=BEGIN_STATE_ID,
        )
        await card_repo.save(card)
        return card

    async def test_demote_card_defaults_to_backlog(self, client, workflow_card):
        response = await client.patch(
            f"/v1/cards/{workflow_card.id.value}/demote",
            json={},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["pre_workflow_stage"] == "backlog"
        assert body["workflow_state_id"] is None

    async def test_demote_card_to_refinement(self, client, workflow_card):
        response = await client.patch(
            f"/v1/cards/{workflow_card.id.value}/demote",
            json={"stage": "refinement"},
        )

        assert response.status_code == 200
        assert response.json()["pre_workflow_stage"] == "refinement"

    async def test_demote_card_to_inbox_returns_422(self, client, workflow_card):
        """INBOX es punto de no-retorno — demote nunca puede ir ahí."""
        response = await client.patch(
            f"/v1/cards/{workflow_card.id.value}/demote",
            json={"stage": "inbox"},
        )

        assert response.status_code == 422

    async def test_demote_card_already_in_preworkflow_returns_422(self, client, card_repo):
        card = Card(
            id=CardId.generate(),
            space_id=SpaceId.generate(),
            title=CardTitle("Card en triage"),
            pre_workflow_stage=PreWorkflowStage.BACKLOG,
            workflow_state_id=None,
        )
        await card_repo.save(card)

        response = await client.patch(
            f"/v1/cards/{card.id.value}/demote",
            json={"stage": "backlog"},
        )

        assert response.status_code == 422

    async def test_demote_card_not_found_returns_404(self, client):
        response = await client.patch(
            f"/v1/cards/{CardId.generate().value}/demote",
            json={"stage": "backlog"},
        )

        assert response.status_code == 404
        assert response.json()["error"] == "card_not_found"
