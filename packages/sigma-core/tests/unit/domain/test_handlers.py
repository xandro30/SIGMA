from sigma_core.task_management.application.error_handlers import handle_domain_error
from sigma_core.task_management.domain.errors import (
    CardNotFoundError,
    InvalidTransitionError,
    WipLimitExceededError,
    SpaceNotFoundError,
)


def test_handle_card_not_found():
    result = handle_domain_error(CardNotFoundError("card not found"))

    assert result.code == "card_not_found"
    assert result.status_code == 404


def test_handle_invalid_transition():
    result = handle_domain_error(InvalidTransitionError("transition not allowed"))

    assert result.code == "invalid_transition"
    assert result.status_code == 422


def test_handle_wip_limit_exceeded():
    result = handle_domain_error(WipLimitExceededError("wip limit reached"))

    assert result.code == "wip_limit_exceeded"
    assert result.status_code == 422


def test_handle_space_not_found():
    result = handle_domain_error(SpaceNotFoundError("space not found"))

    assert result.code == "space_not_found"
    assert result.status_code == 404