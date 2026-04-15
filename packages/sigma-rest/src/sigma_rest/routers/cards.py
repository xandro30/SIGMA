from datetime import date
from fastapi import APIRouter, Depends, Response

from sigma_core.shared_kernel.value_objects import CardId, SpaceId, AreaId, Timestamp
from sigma_core.task_management.domain.value_objects import (
    CardTitle,
    WorkflowStateId,
    ProjectId,
    EpicId,
    Url,
    ChecklistItem,
)
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.task_management.domain.enums import PreWorkflowStage, Priority
from sigma_core.task_management.domain.errors import CardNotFoundError
from sigma_core.task_management.application.use_cases.card.create_card import CreateCard, CreateCardCommand
from sigma_core.task_management.application.use_cases.card.move_card import MoveCard, MoveCardCommand
from sigma_core.task_management.application.use_cases.card.promote_to_workflow import PromoteToWorkflow, PromoteToWorkflowCommand
from sigma_core.task_management.application.use_cases.card.demote_to_pre_workflow import DemoteToPreWorkflow, DemoteToPreWorkflowCommand
from sigma_core.task_management.application.use_cases.card.move_triage_stage import MoveTriageStage, MoveTriageStageCommand  # ← NUEVO
from sigma_core.task_management.application.use_cases.card.update_card import UpdateCard, UpdateCardCommand, UNSET
from sigma_core.task_management.application.use_cases.card.archive_card import ArchiveCard, ArchiveCardCommand
from sigma_core.task_management.application.use_cases.card.delete_card import DeleteCard, DeleteCardCommand
from sigma_core.task_management.application.use_cases.card.assign_area import AssignArea, AssignAreaCommand
from sigma_core.task_management.application.use_cases.card.assign_project import AssignProject, AssignProjectCommand
from sigma_core.task_management.application.use_cases.card.assign_epic import AssignEpic, AssignEpicCommand
from sigma_core.task_management.application.use_cases.card.assign_size import AssignSize, AssignSizeCommand
from sigma_core.task_management.application.use_cases.card.start_timer import StartTimer, StartTimerCommand
from sigma_core.task_management.application.use_cases.card.stop_timer import StopTimer, StopTimerCommand
from sigma_core.task_management.application.use_cases.card.add_work_log_entry import AddWorkLogEntry, AddWorkLogEntryCommand

from sigma_rest.schemas.card_schemas import (
    CreateCardRequest, UpdateCardRequest, MoveCardRequest,
    PromoteCardRequest, DemoteCardRequest, LabelActionRequest,
    TopicActionRequest, UrlActionRequest, AddChecklistItemRequest,
    AddRelatedCardRequest, AssignAreaRequest, AssignProjectRequest, AssignEpicRequest,
    AssignSizeRequest, MoveTriageStageRequest, StartTimerRequest, AddWorkLogRequest, CardResponse,
)
from sigma_rest.mappers.card_mappers import card_to_response
from sigma_rest.dependencies import get_card_repo, get_space_repo, get_area_repo, get_project_repo, get_epic_repo

router = APIRouter(tags=["cards"])


async def _get_card_or_raise(card_repo, card_id: CardId):
    card = await card_repo.get_by_id(card_id)
    if card is None:
        raise CardNotFoundError(f"Card {card_id.value} not found")
    return card


@router.get("/spaces/{space_id}/cards")
async def list_cards(space_id: str, card_repo=Depends(get_card_repo)):
    cards = await card_repo.get_by_space(SpaceId(space_id))
    return {"cards": [card_to_response(c) for c in cards]}


@router.post("/spaces/{space_id}/cards", status_code=201)
async def create_card(
    space_id: str,
    body: CreateCardRequest,
    card_repo=Depends(get_card_repo),
    space_repo=Depends(get_space_repo),
):
    initial_stage = (
        PreWorkflowStage(body.initial_stage)
        if body.initial_stage in [s.value for s in PreWorkflowStage]
        else WorkflowStateId(body.initial_stage)
    )
    use_case = CreateCard(card_repo, space_repo)
    card_id = await use_case.execute(CreateCardCommand(
        space_id=SpaceId(space_id),
        title=CardTitle(body.title),
        initial_stage=initial_stage,
        description=body.description,
        area_id=AreaId(body.area_id) if body.area_id else None,
        project_id=ProjectId(body.project_id) if body.project_id else None,
        epic_id=EpicId(body.epic_id) if body.epic_id else None,
        priority=Priority(body.priority) if body.priority else None,
        labels=set(body.labels),
    ))
    card = await card_repo.get_by_id(card_id)
    return card_to_response(card)


@router.get("/cards/{card_id}")
async def get_card(card_id: str, card_repo=Depends(get_card_repo)):
    card = await card_repo.get_by_id(CardId(card_id))
    return card_to_response(card)


@router.patch("/cards/{card_id}")
async def update_card(
    card_id: str,
    body: UpdateCardRequest,
    card_repo=Depends(get_card_repo),
    area_repo=Depends(get_area_repo),
    epic_repo=Depends(get_epic_repo),
):
    sent = body.model_fields_set
    use_case = UpdateCard(card_repo, area_repo, epic_repo)
    await use_case.execute(UpdateCardCommand(
        card_id=CardId(card_id),
        title=CardTitle(body.title) if body.title else None,
        description=body.description,
        priority=Priority(body.priority) if body.priority else None,
        due_date=date.fromisoformat(body.due_date) if body.due_date else None,
        area_id=AreaId(body.area_id) if body.area_id else None if "area_id" in sent else UNSET,
        epic_id=EpicId(body.epic_id) if body.epic_id else None if "epic_id" in sent else UNSET,
        labels=set(body.labels) if "labels" in sent and body.labels is not None else None,
    ))
    card = await card_repo.get_by_id(CardId(card_id))
    return card_to_response(card)


@router.delete("/cards/{card_id}", status_code=204)
async def delete_card(card_id: str, card_repo=Depends(get_card_repo)):
    use_case = DeleteCard(card_repo)
    await use_case.execute(DeleteCardCommand(card_id=CardId(card_id)))
    return Response(status_code=204)


@router.patch("/cards/{card_id}/move")
async def move_card(
    card_id: str,
    body: MoveCardRequest,
    card_repo=Depends(get_card_repo),
    space_repo=Depends(get_space_repo),
):
    use_case = MoveCard(card_repo, space_repo)
    await use_case.execute(MoveCardCommand(
        card_id=CardId(card_id),
        target_state_id=WorkflowStateId(body.target_state_id),
    ))
    card = await card_repo.get_by_id(CardId(card_id))
    return card_to_response(card)


@router.patch("/cards/{card_id}/promote")
async def promote_card(
    card_id: str,
    body: PromoteCardRequest,
    card_repo=Depends(get_card_repo),
    space_repo=Depends(get_space_repo),
):
    use_case = PromoteToWorkflow(card_repo, space_repo)
    await use_case.execute(PromoteToWorkflowCommand(
        card_id=CardId(card_id),
        target_state_id=WorkflowStateId(body.target_state_id) if body.target_state_id else None,
    ))
    card = await card_repo.get_by_id(CardId(card_id))
    return card_to_response(card)


@router.patch("/cards/{card_id}/demote", response_model=CardResponse)
async def demote_card(
    card_id: str,
    body: DemoteCardRequest,
    card_repo=Depends(get_card_repo),
):
    """Workflow → Triage. Solo 'refinement' o 'backlog'. Nunca 'inbox'."""
    use_case = DemoteToPreWorkflow(card_repo)
    await use_case.execute(DemoteToPreWorkflowCommand(
        card_id=CardId(card_id),
        stage=PreWorkflowStage(body.stage),
    ))
    card = await card_repo.get_by_id(CardId(card_id))
    return card_to_response(card)


@router.patch("/cards/{card_id}/triage-stage", response_model=CardResponse)
async def move_triage_stage(
    card_id: str,
    body: MoveTriageStageRequest,
    card_repo=Depends(get_card_repo),
):
    """Mover dentro de Triage. Inbox solo si la card está actualmente en Inbox."""
    use_case = MoveTriageStage(card_repo)
    await use_case.execute(MoveTriageStageCommand(
        card_id=CardId(card_id),
        target_stage=PreWorkflowStage(body.stage),
    ))
    card = await card_repo.get_by_id(CardId(card_id))
    return card_to_response(card)


@router.post("/cards/{card_id}/archive")
async def archive_card(card_id: str, card_repo=Depends(get_card_repo)):
    use_case = ArchiveCard(card_repo)
    await use_case.execute(ArchiveCardCommand(card_id=CardId(card_id)))
    card = await card_repo.get_by_id(CardId(card_id))
    return card_to_response(card)


@router.patch("/cards/{card_id}/labels")
async def manage_label(
    card_id: str,
    body: LabelActionRequest,
    card_repo=Depends(get_card_repo),
):
    card = await card_repo.get_by_id(CardId(card_id))
    if body.action == "add":
        card.add_label(body.label)
    else:
        card.remove_label(body.label)
    await card_repo.save(card)
    return card_to_response(card)


@router.patch("/cards/{card_id}/topics")
async def manage_topic(
    card_id: str,
    body: TopicActionRequest,
    card_repo=Depends(get_card_repo),
):
    card = await card_repo.get_by_id(CardId(card_id))
    if body.action == "add":
        card.add_topic(body.topic)
    else:
        card.remove_topic(body.topic)
    await card_repo.save(card)
    return card_to_response(card)


@router.patch("/cards/{card_id}/urls")
async def manage_url(
    card_id: str,
    body: UrlActionRequest,
    card_repo=Depends(get_card_repo),
):
    card = await card_repo.get_by_id(CardId(card_id))
    if body.action == "add":
        card.add_url(Url(body.url))
    else:
        card.remove_url(Url(body.url))
    await card_repo.save(card)
    return card_to_response(card)


@router.post("/cards/{card_id}/checklist")
async def add_checklist_item(
    card_id: str,
    body: AddChecklistItemRequest,
    card_repo=Depends(get_card_repo),
):
    card = await card_repo.get_by_id(CardId(card_id))
    card.add_checklist_item(ChecklistItem(body.text))
    await card_repo.save(card)
    return card_to_response(card)


@router.patch("/cards/{card_id}/checklist/{text}")
async def toggle_checklist_item(
    card_id: str,
    text: str,
    card_repo=Depends(get_card_repo),
):
    card = await card_repo.get_by_id(CardId(card_id))
    card.toggle_checklist_item(text)
    await card_repo.save(card)
    return card_to_response(card)


@router.delete("/cards/{card_id}/checklist/{text}")
async def remove_checklist_item(
    card_id: str,
    text: str,
    card_repo=Depends(get_card_repo),
):
    card = await card_repo.get_by_id(CardId(card_id))
    card.remove_checklist_item(text)
    await card_repo.save(card)
    return card_to_response(card)


@router.post("/cards/{card_id}/related")
async def add_related_card(
    card_id: str,
    body: AddRelatedCardRequest,
    card_repo=Depends(get_card_repo),
):
    card = await card_repo.get_by_id(CardId(card_id))
    card.add_related_card(CardId(body.related_card_id))
    await card_repo.save(card)
    return card_to_response(card)


@router.delete("/cards/{card_id}/related/{related_card_id}", status_code=204)
async def remove_related_card(
    card_id: str,
    related_card_id: str,
    card_repo=Depends(get_card_repo),
):
    card = await card_repo.get_by_id(CardId(card_id))
    card.remove_related_card(CardId(related_card_id))
    await card_repo.save(card)
    return Response(status_code=204)


@router.patch("/cards/{card_id}/area")
async def assign_area(
    card_id: str,
    body: AssignAreaRequest,
    card_repo=Depends(get_card_repo),
    area_repo=Depends(get_area_repo),
):
    use_case = AssignArea(card_repo, area_repo)
    await use_case.execute(AssignAreaCommand(
        card_id=CardId(card_id),
        area_id=AreaId(body.area_id) if body.area_id else None,
    ))
    card = await card_repo.get_by_id(CardId(card_id))
    return card_to_response(card)


@router.patch("/cards/{card_id}/project")
async def assign_project(
    card_id: str,
    body: AssignProjectRequest,
    card_repo=Depends(get_card_repo),
    project_repo=Depends(get_project_repo),
):
    use_case = AssignProject(card_repo, project_repo)
    await use_case.execute(AssignProjectCommand(
        card_id=CardId(card_id),
        project_id=ProjectId(body.project_id) if body.project_id else None,
    ))
    card = await card_repo.get_by_id(CardId(card_id))
    return card_to_response(card)


@router.patch("/cards/{card_id}/epic")
async def assign_epic(
    card_id: str,
    body: AssignEpicRequest,
    card_repo=Depends(get_card_repo),
    epic_repo=Depends(get_epic_repo),
):
    use_case = AssignEpic(card_repo, epic_repo)
    await use_case.execute(AssignEpicCommand(
        card_id=CardId(card_id),
        epic_id=EpicId(body.epic_id) if body.epic_id else None,
    ))
    card = await card_repo.get_by_id(CardId(card_id))
    return card_to_response(card)


@router.patch("/cards/{card_id}/size", response_model=CardResponse)
async def assign_size(
    card_id: str,
    body: AssignSizeRequest,
    card_repo=Depends(get_card_repo),
):
    use_case = AssignSize(card_repo)
    await use_case.execute(AssignSizeCommand(
        card_id=CardId(card_id),
        size=CardSize(body.size) if body.size else None,
    ))
    card = await _get_card_or_raise(card_repo, CardId(card_id))
    return card_to_response(card)


@router.post("/cards/{card_id}/timer/start", response_model=CardResponse)
async def start_timer(
    card_id: str,
    body: StartTimerRequest = StartTimerRequest(),
    card_repo=Depends(get_card_repo),
):
    use_case = StartTimer(card_repo)
    await use_case.execute(StartTimerCommand(
        card_id=CardId(card_id),
        now=Timestamp.now(),
        description=body.description,
    ))
    card = await _get_card_or_raise(card_repo, CardId(card_id))
    return card_to_response(card)


@router.post("/cards/{card_id}/timer/stop", response_model=CardResponse)
async def stop_timer(
    card_id: str,
    card_repo=Depends(get_card_repo),
):
    use_case = StopTimer(card_repo)
    await use_case.execute(StopTimerCommand(
        card_id=CardId(card_id),
        now=Timestamp.now(),
    ))
    card = await _get_card_or_raise(card_repo, CardId(card_id))
    return card_to_response(card)

@router.post("/cards/{card_id}/work-log", status_code=204)
async def add_work_log(
    card_id: str,
    body: AddWorkLogRequest,
    card_repo=Depends(get_card_repo),
):
    await AddWorkLogEntry(card_repo).execute(AddWorkLogEntryCommand(
        card_id=CardId(card_id),
        description=body.description,
        minutes=body.minutes,
    ))
