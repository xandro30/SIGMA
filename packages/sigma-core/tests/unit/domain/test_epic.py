import pytest
from sigma_core.task_management.domain.epic import Epic
from sigma_core.task_management.domain.value_objects import (
    EpicId, SpaceId, ProjectId, AreaId, Timestamp,
)


def test_epic_is_created_correctly():
    epic_id = EpicId.generate()
    space_id = SpaceId.generate()
    project_id = ProjectId.generate()
    area_id = AreaId.generate()
    created_at = Timestamp.now()

    epic = Epic(id=epic_id, space_id=space_id, project_id=project_id, area_id=area_id, name="Auth Module")

    assert epic.id == epic_id
    assert epic.space_id == space_id
    assert epic.project_id == project_id
    assert epic.area_id == area_id
    assert epic.name == "Auth Module"
    assert epic.description is None


def test_epic_empty_name_raises_value_error():
    with pytest.raises(ValueError):
        Epic(
            id=EpicId.generate(),
            space_id=SpaceId.generate(),
            project_id=ProjectId.generate(),
            area_id=AreaId.generate(),
            name="",
        )


def test_epic_rename_updates_name():
    epic = Epic(
        id=EpicId.generate(),
        space_id=SpaceId.generate(),
        project_id=ProjectId.generate(),
        area_id=AreaId.generate(),
        name="Auth Module",
    )

    epic.rename("Security Module")

    assert epic.name == "Security Module"


def test_epic_update_description_updates_description():
    epic = Epic(
        id=EpicId.generate(),
        space_id=SpaceId.generate(),
        project_id=ProjectId.generate(),
        area_id=AreaId.generate(),
        name="Auth Module",
    )

    epic.update_description("Sistema de autenticación completo")

    assert epic.description == "Sistema de autenticación completo"