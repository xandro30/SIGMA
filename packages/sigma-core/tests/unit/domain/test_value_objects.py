# tests/unit/domain/test_value_objects.py

import uuid
import pytest
from sigma_core.task_management.domain.value_objects import (
    CardId, SpaceId, WorkflowStateId, AreaId, ProjectId, EpicId,
    CardTitle, SpaceName, Url, ChecklistItem,
)


# ── CardTitle ─────────────────────────────────────────────────────

def test_card_title_se_crea_con_texto_valido():
    text = "Implementar login con Google"

    result = CardTitle(text)

    assert result.value == text


def test_card_title_normaliza_espacios_al_inicio_y_final():
    text = "  Tarea con espacios  "

    result = CardTitle(text)

    assert result.value == "Tarea con espacios"


def test_card_title_vacio_lanza_value_error():
    with pytest.raises(ValueError):
        CardTitle("")


def test_card_title_solo_espacios_lanza_value_error():
    with pytest.raises(ValueError):
        CardTitle("   ")


def test_card_title_de_255_caracteres_es_valido():
    text = "x" * 255

    result = CardTitle(text)

    assert len(result.value) == 255


def test_card_title_de_256_caracteres_lanza_value_error():
    with pytest.raises(ValueError):
        CardTitle("x" * 256)


def test_card_title_es_inmutable():
    result = CardTitle("Mi tarea")

    with pytest.raises(Exception):
        result.value = "Otro valor"


def test_dos_card_title_con_mismo_valor_son_iguales():
    assert CardTitle("Mi tarea") == CardTitle("Mi tarea")


def test_dos_card_title_con_distinto_valor_son_distintos():
    assert CardTitle("Tarea A") != CardTitle("Tarea B")


# ── Url ───────────────────────────────────────────────────────────

def test_url_https_valida_se_crea_correctamente():
    url = "https://firebase.google.com/docs"

    result = Url(url)

    assert result.value == url


def test_url_http_valida_se_crea_correctamente():
    url = "http://localhost:8000/api"

    result = Url(url)

    assert result.value == url


def test_url_sin_esquema_lanza_value_error():
    with pytest.raises(ValueError):
        Url("firebase.google.com/docs")


def test_url_con_esquema_ftp_lanza_value_error():
    with pytest.raises(ValueError):
        Url("ftp://files.example.com")


def test_url_vacia_lanza_value_error():
    with pytest.raises(ValueError):
        Url("")


def test_dos_url_con_mismo_valor_son_iguales():
    url = "https://example.com"

    assert Url(url) == Url(url)


# ── ChecklistItem ─────────────────────────────────────────────────

def test_checklist_item_se_crea_sin_completar_por_defecto():
    text = "Revisar documentación"

    result = ChecklistItem(text)

    assert result.done is False


def test_checklist_item_complete_devuelve_nueva_instancia_con_done_true():
    original = ChecklistItem("Revisar documentación", done=False)

    result = original.complete()

    assert result.done is True
    assert result is not original


def test_checklist_item_complete_no_muta_el_original():
    original = ChecklistItem("Revisar documentación", done=False)

    original.complete()

    assert original.done is False


def test_checklist_item_reopen_devuelve_nueva_instancia_con_done_false():
    original = ChecklistItem("Revisar documentación", done=True)

    result = original.reopen()

    assert result.done is False
    assert result is not original


def test_checklist_item_vacio_lanza_value_error():
    with pytest.raises(ValueError):
        ChecklistItem("")


def test_checklist_item_de_500_caracteres_es_valido():
    text = "x" * 500

    result = ChecklistItem(text)

    assert len(result.text) == 500


def test_checklist_item_de_501_caracteres_lanza_value_error():
    with pytest.raises(ValueError):
        ChecklistItem("x" * 501)


def test_checklist_item_normaliza_espacios_al_inicio_y_final():
    text = "  Revisar docs  "

    result = ChecklistItem(text)

    assert result.text == "Revisar docs"


# ── IDs ───────────────────────────────────────────────────────────

def test_card_id_generate_produce_uuid_v4_valido():
    result = CardId.generate()

    parsed = uuid.UUID(result.value, version=4)

    assert str(parsed) == result.value


def test_card_id_con_uuid_valido_se_crea_correctamente():
    value = "550e8400-e29b-41d4-a716-446655440000"

    result = CardId(value)

    assert result.value == value


def test_card_id_con_string_arbitrario_lanza_value_error():
    with pytest.raises(ValueError):
        CardId("no-es-un-uuid")


def test_dos_card_id_con_mismo_uuid_son_iguales():
    value = str(uuid.uuid4())

    assert CardId(value) == CardId(value)


def test_dos_card_id_con_distinto_uuid_son_distintos():
    assert CardId.generate() != CardId.generate()


def test_todos_los_ids_siguen_el_mismo_patron():
    for IdClass in [SpaceId, WorkflowStateId, AreaId, ProjectId, EpicId]:
        value = str(uuid.uuid4())

        assert IdClass(value).value == value

        with pytest.raises(ValueError):
            IdClass("no-es-un-uuid")