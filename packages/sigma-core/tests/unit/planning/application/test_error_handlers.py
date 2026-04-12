from sigma_core.planning.application.error_handlers import (
    handle_planning_error,
)
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
    PlanningCardNotFoundError,
    PlanningDomainError,
    WeekTemplateNotFoundError,
)


class TestNotFoundMapping:
    def test_cycle_not_found(self):
        result = handle_planning_error(CycleNotFoundError("x"))
        assert result.code == "cycle_not_found"
        assert result.status_code == 404

    def test_day_not_found(self):
        result = handle_planning_error(DayNotFoundError("x"))
        assert result.code == "day_not_found"
        assert result.status_code == 404

    def test_block_not_found(self):
        result = handle_planning_error(BlockNotFoundError("x"))
        assert result.code == "block_not_found"
        assert result.status_code == 404

    def test_day_template_not_found(self):
        result = handle_planning_error(DayTemplateNotFoundError("x"))
        assert result.code == "day_template_not_found"
        assert result.status_code == 404

    def test_week_template_not_found(self):
        result = handle_planning_error(WeekTemplateNotFoundError("x"))
        assert result.code == "week_template_not_found"
        assert result.status_code == 404


    def test_planning_card_not_found(self):
        result = handle_planning_error(PlanningCardNotFoundError("x"))
        assert result.code == "card_not_found"
        assert result.status_code == 404


class TestConflictMapping:
    def test_cycle_already_active_incluye_detail(self):
        result = handle_planning_error(
            CycleAlreadyActiveError("space-1", "cycle-1")
        )
        assert result.code == "cycle_already_active"
        assert result.status_code == 409
        assert result.detail == {
            "space_id": "space-1",
            "active_cycle_id": "cycle-1",
        }

    def test_day_not_empty(self):
        result = handle_planning_error(DayNotEmptyError("x"))
        assert result.code == "day_not_empty"
        assert result.status_code == 409

    def test_block_overlap_incluye_block_id(self):
        result = handle_planning_error(BlockOverlapError("block-123"))
        assert result.code == "block_overlap"
        assert result.status_code == 409
        assert result.detail == {"block_id": "block-123"}


class TestUnprocessableMapping:
    def test_invalid_cycle_transition_incluye_detail(self):
        result = handle_planning_error(
            InvalidCycleTransitionError("closed", "active")
        )
        assert result.code == "invalid_cycle_transition"
        assert result.status_code == 422
        assert result.detail == {
            "from_state": "closed",
            "to_state": "active",
        }

    def test_invalid_buffer(self):
        result = handle_planning_error(InvalidBufferError("x"))
        assert result.code == "invalid_buffer"
        assert result.status_code == 422

    def test_invalid_date_range(self):
        result = handle_planning_error(InvalidDateRangeError("x"))
        assert result.code == "invalid_date_range"
        assert result.status_code == 422

    def test_invalid_time_block(self):
        result = handle_planning_error(InvalidTimeBlockError("x"))
        assert result.code == "invalid_time_block"
        assert result.status_code == 422

    def test_invalid_week_start(self):
        result = handle_planning_error(InvalidWeekStartError("x"))
        assert result.code == "invalid_week_start"
        assert result.status_code == 422

    def test_invalid_card_for_eta(self):
        result = handle_planning_error(InvalidCardForEtaError("x"))
        assert result.code == "invalid_card_for_eta"
        assert result.status_code == 422

    def test_budget_not_found_es_422(self):
        """BudgetNotFound describe una condición semántica inválida sobre el
        cycle (el área no tiene budget asignado), no la ausencia de un recurso
        independiente, así que se mapea a 422 en vez de 404."""
        result = handle_planning_error(BudgetNotFoundError("x"))
        assert result.code == "budget_not_found"
        assert result.status_code == 422

    def test_cross_space_reference_incluye_detail(self):
        result = handle_planning_error(
            CrossSpaceReferenceError(
                source_kind="WeekTemplate",
                source_space_id="space-a",
                target_kind="DayTemplate",
                target_space_id="space-b",
            )
        )
        assert result.code == "cross_space_reference"
        assert result.status_code == 422
        assert result.detail == {
            "source_kind": "WeekTemplate",
            "source_space_id": "space-a",
            "target_kind": "DayTemplate",
            "target_space_id": "space-b",
        }


class TestFallback:
    def test_fallback_para_error_no_mapeado(self):
        class CustomPlanningError(PlanningDomainError):
            pass

        result = handle_planning_error(CustomPlanningError("x"))
        assert result.code == "planning_domain_error"
        assert result.status_code == 500
