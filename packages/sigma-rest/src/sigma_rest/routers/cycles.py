from fastapi import APIRouter, Depends, Query, Response

from sigma_core.planning.application.use_cases.cycle.activate_cycle import (
    ActivateCycle,
    ActivateCycleCommand,
)
from sigma_core.planning.application.use_cases.cycle.close_cycle import (
    CloseCycle,
    CloseCycleCommand,
)
from sigma_core.planning.application.use_cases.cycle.create_cycle import (
    CreateCycle,
    CreateCycleCommand,
)
from sigma_core.planning.application.use_cases.cycle.delete_cycle import (
    DeleteCycle,
    DeleteCycleCommand,
)
from sigma_core.planning.application.use_cases.cycle.remove_area_budget import (
    RemoveAreaBudget,
    RemoveAreaBudgetCommand,
)
from sigma_core.planning.application.use_cases.cycle.set_area_budget import (
    SetAreaBudget,
    SetAreaBudgetCommand,
)
from sigma_core.planning.application.use_cases.cycle.set_buffer_percentage import (
    SetBufferPercentage,
    SetBufferPercentageCommand,
)
from sigma_core.planning.domain.enums import CycleType
from sigma_core.planning.domain.errors import CycleNotFoundError
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.value_objects import AreaId, Minutes, SpaceId, Timestamp
from sigma_rest.dependencies import get_cycle_repo, get_event_bus
from sigma_rest.mappers.cycle_mappers import cycle_to_response
from sigma_rest.routers._helpers import require_cycle
from sigma_rest.schemas.cycle_schemas import (
    CreateCycleRequest,
    SetAreaBudgetRequest,
    SetBufferPercentageRequest,
)


router = APIRouter(prefix="/spaces/{space_id}/cycles", tags=["cycles"])


@router.get("")
async def list_cycles(
    space_id: str,
    cycle_repo=Depends(get_cycle_repo),
):
    cycles = await cycle_repo.list_by_space(SpaceId(space_id))
    return {"cycles": [cycle_to_response(c) for c in cycles]}


@router.post("", status_code=201)
async def create_cycle(
    space_id: str,
    body: CreateCycleRequest,
    cycle_repo=Depends(get_cycle_repo),
):
    use_case = CreateCycle(cycle_repo)
    cycle_id = await use_case.execute(
        CreateCycleCommand(
            space_id=SpaceId(space_id),
            name=body.name,
            date_range=DateRange(
                start=body.date_range.start, end=body.date_range.end
            ),
            cycle_type=CycleType(body.cycle_type.value),
        )
    )
    if body.buffer_percentage is not None:
        await SetBufferPercentage(cycle_repo).execute(
            SetBufferPercentageCommand(
                cycle_id=cycle_id, percentage=body.buffer_percentage
            )
        )
    cycle = await require_cycle(cycle_repo, cycle_id)
    return cycle_to_response(cycle)


@router.get("/active")
async def get_active_cycle(
    space_id: str,
    cycle_type: str | None = Query(default=None),
    cycle_repo=Depends(get_cycle_repo),
):
    ct = CycleType(cycle_type) if cycle_type else None
    cycle = await cycle_repo.get_active_by_space(SpaceId(space_id), ct)
    if cycle is None:
        raise CycleNotFoundError(f"Space {space_id} has no active cycle")
    return cycle_to_response(cycle)


@router.get("/active/all")
async def list_active_cycles(
    space_id: str,
    cycle_repo=Depends(get_cycle_repo),
):
    cycles = await cycle_repo.list_active_by_space(SpaceId(space_id))
    return {"cycles": [cycle_to_response(c) for c in cycles]}


@router.get("/{cycle_id}")
async def get_cycle(
    space_id: str,
    cycle_id: str,
    cycle_repo=Depends(get_cycle_repo),
):
    cycle = await require_cycle(cycle_repo, CycleId(cycle_id))
    return cycle_to_response(cycle)


@router.post("/{cycle_id}/activate")
async def activate_cycle(
    space_id: str,
    cycle_id: str,
    cycle_repo=Depends(get_cycle_repo),
):
    use_case = ActivateCycle(cycle_repo)
    await use_case.execute(ActivateCycleCommand(cycle_id=CycleId(cycle_id)))
    cycle = await require_cycle(cycle_repo, CycleId(cycle_id))
    return cycle_to_response(cycle)


@router.post("/{cycle_id}/close")
async def close_cycle(
    space_id: str,
    cycle_id: str,
    cycle_repo=Depends(get_cycle_repo),
    event_bus=Depends(get_event_bus),
):
    use_case = CloseCycle(cycle_repo, event_bus)
    await use_case.execute(
        CloseCycleCommand(cycle_id=CycleId(cycle_id), now=Timestamp.now())
    )
    cycle = await require_cycle(cycle_repo, CycleId(cycle_id))
    return cycle_to_response(cycle)


@router.put("/{cycle_id}/budgets")
async def set_area_budget(
    space_id: str,
    cycle_id: str,
    body: SetAreaBudgetRequest,
    cycle_repo=Depends(get_cycle_repo),
):
    use_case = SetAreaBudget(cycle_repo)
    await use_case.execute(
        SetAreaBudgetCommand(
            cycle_id=CycleId(cycle_id),
            area_id=AreaId(body.area_id),
            minutes=Minutes(body.minutes),
        )
    )
    cycle = await require_cycle(cycle_repo, CycleId(cycle_id))
    return cycle_to_response(cycle)


@router.delete("/{cycle_id}/budgets/{area_id}")
async def remove_area_budget(
    space_id: str,
    cycle_id: str,
    area_id: str,
    cycle_repo=Depends(get_cycle_repo),
):
    use_case = RemoveAreaBudget(cycle_repo)
    await use_case.execute(
        RemoveAreaBudgetCommand(
            cycle_id=CycleId(cycle_id), area_id=AreaId(area_id)
        )
    )
    cycle = await require_cycle(cycle_repo, CycleId(cycle_id))
    return cycle_to_response(cycle)


@router.patch("/{cycle_id}/buffer")
async def set_buffer_percentage(
    space_id: str,
    cycle_id: str,
    body: SetBufferPercentageRequest,
    cycle_repo=Depends(get_cycle_repo),
):
    use_case = SetBufferPercentage(cycle_repo)
    await use_case.execute(
        SetBufferPercentageCommand(
            cycle_id=CycleId(cycle_id),
            percentage=body.buffer_percentage,
        )
    )
    cycle = await require_cycle(cycle_repo, CycleId(cycle_id))
    return cycle_to_response(cycle)


@router.delete("/{cycle_id}", status_code=204)
async def delete_cycle(
    space_id: str,
    cycle_id: str,
    cycle_repo=Depends(get_cycle_repo),
):
    use_case = DeleteCycle(cycle_repo)
    await use_case.execute(DeleteCycleCommand(cycle_id=CycleId(cycle_id)))
    return Response(status_code=204)
