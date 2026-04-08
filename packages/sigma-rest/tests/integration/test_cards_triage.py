import pytest
from sigma_core.task_management.domain.value_objects import CardId


@pytest.mark.asyncio
async def test_move_triage_stage_inbox_to_refinement(client, card_in_inbox):
    response = await client.patch(
        f"/v1/cards/{card_in_inbox.id.value}/triage-stage",
        json={"stage": "refinement"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["pre_workflow_stage"] == "refinement"
    assert body["id"] == card_in_inbox.id.value


@pytest.mark.asyncio
async def test_move_triage_stage_same_stage_returns_409(client, card_in_inbox):
    response = await client.patch(
        f"/v1/cards/{card_in_inbox.id.value}/triage-stage",
        json={"stage": "inbox"},
    )

    assert response.status_code == 409
    assert response.json()["error"] == "already_in_stage"


@pytest.mark.asyncio
async def test_move_triage_stage_inbox_not_allowed_returns_422(client, card_in_refinement):
    response = await client.patch(
        f"/v1/cards/{card_in_refinement.id.value}/triage-stage",
        json={"stage": "inbox"},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "inbox_not_allowed"


@pytest.mark.asyncio
async def test_move_triage_stage_card_in_workflow_returns_422(client, card_in_workflow):
    response = await client.patch(
        f"/v1/cards/{card_in_workflow.id.value}/triage-stage",
        json={"stage": "refinement"},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "card_not_in_triage"


@pytest.mark.asyncio
async def test_move_triage_stage_card_not_found_returns_404(client):
    response = await client.patch(
        f"/v1/cards/{CardId.generate().value}/triage-stage",
        json={"stage": "refinement"},
    )

    assert response.status_code == 404
    assert response.json()["error"] == "card_not_found"
