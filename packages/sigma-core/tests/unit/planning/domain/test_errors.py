import pytest

from sigma_core.planning.domain.errors import (
    BlockNotFoundError,
    BlockOverlapError,
    BudgetNotFoundError,
    CrossSpaceReferenceError,
    CycleAlreadyActiveError,
    CycleNotFoundError,
    DayNotEmptyError,
    DayNotFoundError,
    DayTemplateNotFoundError,
    InvalidBufferError,
    InvalidCardForEtaError,
    InvalidCycleTransitionError,
    InvalidDateRangeError,
    InvalidTimeBlockError,
    InvalidWeekStartError,
    PlanningDomainError,
    WeekTemplateNotFoundError,
)
from sigma_core.shared_kernel.errors import SigmaDomainError


PLANNING_ERROR_CLASSES = [
    CycleNotFoundError,
    CycleAlreadyActiveError,
    InvalidCycleTransitionError,
    InvalidBufferError,
    BudgetNotFoundError,
    InvalidDateRangeError,
    DayNotFoundError,
    DayNotEmptyError,
    BlockNotFoundError,
    BlockOverlapError,
    InvalidTimeBlockError,
    DayTemplateNotFoundError,
    WeekTemplateNotFoundError,
    InvalidWeekStartError,
    InvalidCardForEtaError,
    CrossSpaceReferenceError,
]


def test_planning_domain_error_extiende_sigma_domain_error():
    assert issubclass(PlanningDomainError, SigmaDomainError)


@pytest.mark.parametrize("error_cls", PLANNING_ERROR_CLASSES)
def test_errores_de_planning_extienden_planning_domain_error(error_cls):
    assert issubclass(error_cls, PlanningDomainError)


def test_cycle_already_active_error_conserva_payload():
    exc = CycleAlreadyActiveError(
        space_id="space-1",
        active_cycle_id="cycle-1",
    )
    assert exc.space_id == "space-1"
    assert exc.active_cycle_id == "cycle-1"
    # También es representable como string no vacía
    assert "space-1" in str(exc)
    assert "cycle-1" in str(exc)


def test_invalid_cycle_transition_error_conserva_payload():
    exc = InvalidCycleTransitionError(from_state="closed", to_state="active")
    assert exc.from_state == "closed"
    assert exc.to_state == "active"


def test_block_overlap_error_conserva_block_id():
    exc = BlockOverlapError(block_id="block-123")
    assert exc.block_id == "block-123"


def test_invalid_buffer_error_puede_construirse_con_mensaje():
    exc = InvalidBufferError("buffer fuera de rango 0..100")
    assert "buffer" in str(exc)


def test_invalid_date_range_error_puede_construirse_con_mensaje():
    exc = InvalidDateRangeError("start > end")
    assert "start" in str(exc)
