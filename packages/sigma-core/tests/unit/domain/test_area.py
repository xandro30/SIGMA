import pytest
from sigma_core.task_management.domain.area import Area
from sigma_core.task_management.domain.value_objects import AreaId, Timestamp


def test_area_is_created_correctly():
    area_id = AreaId.generate()

    area = Area(id=area_id, name="Work",)

    assert area.id == area_id
    assert area.name == "Work"
    assert area.description is None
    assert area.objectives == []


def test_area_empty_name_raises_value_error():
    with pytest.raises(ValueError):
        Area(
            id=AreaId.generate(),
            name="",
            created_at=Timestamp.now(),
            updated_at=Timestamp.now(),
        )


def test_area_rename_updates_name():
    area = Area(id=AreaId.generate(), name="Work", created_at=Timestamp.now(), updated_at=Timestamp.now())

    area.rename("Sngular")

    assert area.name == "Sngular"


def test_area_add_objective_adds_to_list():
    area = Area(
        id=AreaId.generate(),
        name="Work",
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )

    area.add_objective("PSOE cert Q2")

    assert "PSOE cert Q2" in area.objectives


def test_area_remove_objective_removes_from_list():
    area = Area(
        id=AreaId.generate(),
        name="Work",
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )
    area.add_objective("PSOE cert Q2")

    area.remove_objective("PSOE cert Q2")

    assert "PSOE cert Q2" not in area.objectives