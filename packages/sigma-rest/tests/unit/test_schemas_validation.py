import pytest
from pydantic import ValidationError

from sigma_rest.schemas.card_schemas import AssignSizeRequest
from sigma_rest.schemas.space_schemas import SetSizeMappingRequest


# ── AssignSizeRequest ─────────────────────────────────────────────

def test_assign_size_request_acepta_literales_validos():
    for size in ["xxs", "xs", "s", "m", "l", "xl", "xxl"]:
        result = AssignSizeRequest(size=size)
        assert result.size == size


def test_assign_size_request_acepta_none():
    result = AssignSizeRequest(size=None)

    assert result.size is None


def test_assign_size_request_rechaza_valor_invalido():
    with pytest.raises(ValidationError):
        AssignSizeRequest(size="huge")


def test_assign_size_request_rechaza_vacio():
    with pytest.raises(ValidationError):
        AssignSizeRequest(size="")


# ── SetSizeMappingRequest ─────────────────────────────────────────

def _valid_mapping() -> dict[str, int]:
    return {
        "xxs": 30,
        "xs": 60,
        "s": 120,
        "m": 240,
        "l": 480,
        "xl": 960,
        "xxl": 1920,
    }


def test_set_size_mapping_request_acepta_mapping_valido():
    result = SetSizeMappingRequest(mapping=_valid_mapping())

    assert result.mapping is not None
    assert result.mapping["m"] == 240


def test_set_size_mapping_request_acepta_none():
    result = SetSizeMappingRequest(mapping=None)

    assert result.mapping is None


def test_set_size_mapping_request_rechaza_valor_negativo():
    mapping = _valid_mapping()
    mapping["xxs"] = -1

    with pytest.raises(ValidationError):
        SetSizeMappingRequest(mapping=mapping)


def test_set_size_mapping_request_rechaza_mas_de_siete_entradas():
    mapping = _valid_mapping()
    mapping["extra"] = 10

    with pytest.raises(ValidationError):
        SetSizeMappingRequest(mapping=mapping)
