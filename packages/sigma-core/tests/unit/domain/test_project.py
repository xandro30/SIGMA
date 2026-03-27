import pytest

from sigma_core.task_management.domain.project import Project
from sigma_core.task_management.domain.enums import ProjectStatus
from sigma_core.task_management.domain.value_objects import ProjectId, AreaId, Timestamp


def test_project_is_created_correctly():
    project_id = ProjectId.generate()
    area_id = AreaId.generate()
    created_at = Timestamp.now()

    project = Project(
        id=project_id,
        name="N3 SecOps",
        area_id=area_id,
        status=ProjectStatus.ACTIVE,
        created_at=created_at,
        updated_at=created_at,
    )

    assert project.id == project_id
    assert project.name == "N3 SecOps"
    assert project.area_id == area_id
    assert project.status == ProjectStatus.ACTIVE
    assert project.description is None
    assert project.objectives == []


def test_project_empty_name_raises_value_error():
    with pytest.raises(ValueError):
        Project(id=ProjectId.generate(), name="", area_id=AreaId.generate(), status=ProjectStatus.ACTIVE)


def test_project_rename_updates_name():
    project = Project(id=ProjectId.generate(), name="N3 SecOps", area_id=AreaId.generate(), status=ProjectStatus.ACTIVE)

    project.rename("GitSync Automation")

    assert project.name == "GitSync Automation"


def test_project_change_status_updates_status():
    project = Project(id=ProjectId.generate(), name="N3 SecOps", area_id=AreaId.generate(), status=ProjectStatus.ACTIVE)

    project.change_status(ProjectStatus.COMPLETED)

    assert project.status == ProjectStatus.COMPLETED


def test_project_add_objective_adds_to_list():
    project = Project(id=ProjectId.generate(), name="N3 SecOps", area_id=AreaId.generate(), status=ProjectStatus.ACTIVE)

    project.add_objective("YARA-L migration")

    assert "YARA-L migration" in project.objectives