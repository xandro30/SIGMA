import pytest
from sigma_core.task_management.domain.entities.area import Area
from sigma_core.shared_kernel.value_objects import AreaId, Timestamp


def test_area_is_created_correctly():
    area_id = AreaId.generate()

    area = Area(id=area_id, name="Work",)

    assert area.id == area_id
    assert area.name == "Work"
    assert area.description is None
    assert area.objectives is None


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


def test_area_update_objectives_sets_text():
    area = Area(
        id=AreaId.generate(),
        name="Work",
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )

    area.update_objectives("GCP cert Q2")

    assert area.objectives == "GCP cert Q2"


def test_area_update_objectives_clears_with_none():
    area = Area(
        id=AreaId.generate(),
        name="Work",
        objectives="GCP cert Q2",
        created_at=Timestamp.now(),
        updated_at=Timestamp.now(),
    )

    area.update_objectives(None)

    assert area.objectives is None