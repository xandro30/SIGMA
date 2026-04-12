import pytest
from datetime import datetime
import uuid

from sigma_core.shared_kernel.enums import CardSize
from sigma_core.shared_kernel.value_objects import (
    CardId,
    SpaceId,
    AreaId,
    Timestamp,
    Minutes,
    SizeMapping,
)
from sigma_core.task_management.domain.value_objects import (
    WorkflowStateId,
    ProjectId,
    EpicId,
    CardTitle,
    Url,
    ChecklistItem,
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


def test_timestamp_now_creates_madrid_timezone():
    result = Timestamp.now()

    assert result.value.tzinfo is not None
    assert result.value.tzinfo.key == "Europe/Madrid"


def test_timestamp_naive_datetime_raises_value_error():

    with pytest.raises(ValueError):
        Timestamp(datetime(2026, 1, 1))


# ── CardSize ──────────────────────────────────────────────────────

def test_card_size_tiene_los_siete_valores_esperados():
    expected = {"xxs", "xs", "s", "m", "l", "xl", "xxl"}

    actual = {size.value for size in CardSize}

    assert actual == expected


def test_card_size_valores_en_orden_ascendente_de_esfuerzo():
    order = [
        CardSize.XXS, CardSize.XS, CardSize.S,
        CardSize.M, CardSize.L, CardSize.XL, CardSize.XXL,
    ]

    assert len(order) == len(CardSize)


# ── Minutes ───────────────────────────────────────────────────────

def test_minutes_cero_es_valido():
    result = Minutes(0)

    assert result.value == 0


def test_minutes_positivo_es_valido():
    result = Minutes(120)

    assert result.value == 120


def test_minutes_negativo_lanza_value_error():
    with pytest.raises(ValueError):
        Minutes(-1)


def test_minutes_suma_devuelve_nueva_instancia():
    a = Minutes(30)
    b = Minutes(45)

    result = a + b

    assert result == Minutes(75)
    assert a.value == 30


def test_dos_minutes_con_mismo_valor_son_iguales():
    assert Minutes(60) == Minutes(60)


def test_minutes_es_inmutable():
    result = Minutes(10)

    with pytest.raises(Exception):
        result.value = 20


# ── SizeMapping ───────────────────────────────────────────────────

def test_size_mapping_default_tiene_una_entrada_por_cada_card_size():
    mapping = SizeMapping.default()

    for size in CardSize:
        assert mapping.get_minutes(size) is not None


def test_size_mapping_default_values():
    mapping = SizeMapping.default()

    assert mapping.get_minutes(CardSize.XXS) == Minutes(60)
    assert mapping.get_minutes(CardSize.XS) == Minutes(120)
    assert mapping.get_minutes(CardSize.S) == Minutes(240)
    assert mapping.get_minutes(CardSize.M) == Minutes(480)
    assert mapping.get_minutes(CardSize.L) == Minutes(960)
    assert mapping.get_minutes(CardSize.XL) == Minutes(1920)
    assert mapping.get_minutes(CardSize.XXL) == Minutes(3840)


def test_size_mapping_con_entrada_faltante_lanza_value_error():
    incomplete = {CardSize.XXS: Minutes(60)}

    with pytest.raises(ValueError):
        SizeMapping(entries=incomplete)


def test_size_mapping_custom_valores_validos():
    entries = {
        CardSize.XXS: Minutes(30),
        CardSize.XS: Minutes(60),
        CardSize.S: Minutes(120),
        CardSize.M: Minutes(240),
        CardSize.L: Minutes(480),
        CardSize.XL: Minutes(960),
        CardSize.XXL: Minutes(1920),
    }

    mapping = SizeMapping(entries=entries)

    assert mapping.get_minutes(CardSize.M) == Minutes(240)


def test_dos_size_mapping_con_mismas_entradas_son_iguales():
    a = SizeMapping.default()
    b = SizeMapping.default()

    assert a == b


def test_size_mapping_to_primitive_devuelve_dict_ordenado_canonicamente():
    mapping = SizeMapping.default()

    primitive = mapping.to_primitive()

    assert list(primitive.keys()) == ["xxs", "xs", "s", "m", "l", "xl", "xxl"]
    assert primitive["m"] == 480
    assert primitive["xxl"] == 3840


def test_size_mapping_to_primitive_orden_es_canonico_independiente_del_insert_order():
    reversed_entries = {
        CardSize.XXL: Minutes(3840),
        CardSize.XL: Minutes(1920),
        CardSize.L: Minutes(960),
        CardSize.M: Minutes(480),
        CardSize.S: Minutes(240),
        CardSize.XS: Minutes(120),
        CardSize.XXS: Minutes(60),
    }
    mapping = SizeMapping(entries=reversed_entries)

    primitive = mapping.to_primitive()

    assert list(primitive.keys()) == ["xxs", "xs", "s", "m", "l", "xl", "xxl"]


def test_size_mapping_from_primitive_reconstruye_valor():
    primitive = {
        "xxs": 30,
        "xs": 60,
        "s": 120,
        "m": 240,
        "l": 480,
        "xl": 960,
        "xxl": 1920,
    }

    mapping = SizeMapping.from_primitive(primitive)

    assert mapping.get_minutes(CardSize.M) == Minutes(240)
    assert mapping.get_minutes(CardSize.XXL) == Minutes(1920)


def test_size_mapping_from_primitive_con_key_invalida_lanza_value_error():
    with pytest.raises(ValueError):
        SizeMapping.from_primitive({"foo": 30})


def test_size_mapping_from_primitive_incompleto_lanza_value_error():
    with pytest.raises(ValueError):
        SizeMapping.from_primitive({"xxs": 30, "s": 120})


def test_size_mapping_from_primitive_con_valor_negativo_lanza_value_error():
    complete_but_negative = {
        "xxs": -1,
        "xs": 60,
        "s": 120,
        "m": 240,
        "l": 480,
        "xl": 960,
        "xxl": 1920,
    }

    with pytest.raises(ValueError):
        SizeMapping.from_primitive(complete_but_negative)


def test_size_mapping_round_trip_primitive():
    original = SizeMapping.default()

    round_tripped = SizeMapping.from_primitive(original.to_primitive())

    assert round_tripped == original