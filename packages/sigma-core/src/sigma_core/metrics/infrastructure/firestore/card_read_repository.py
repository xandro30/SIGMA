"""MetricsCardReader — projection de cards completadas a CardSnapshot."""
from __future__ import annotations

from datetime import datetime, time
from typing import Any

from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.metrics.domain.value_objects import CardSnapshot
from sigma_core.planning.domain.value_objects import DateRange
from sigma_core.shared_kernel.config import get_app_timezone
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.shared_kernel.value_objects import AreaId, CardId, SpaceId, Timestamp
from sigma_core.task_management.domain.value_objects import EpicId, ProjectId


class FirestoreMetricsCardReader:
    COLLECTION = "cards"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def list_completed_in_range(
        self, space_id: SpaceId, date_range: DateRange
    ) -> list[CardSnapshot]:
        tz = get_app_timezone()
        start_dt = datetime.combine(date_range.start, time.min, tzinfo=tz)
        end_dt = datetime.combine(date_range.end, time.max, tzinfo=tz)
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .where(filter=FieldFilter("completed_at", ">=", start_dt))
            .where(filter=FieldFilter("completed_at", "<=", end_dt))
            .get()
        )
        return [_project(self._snapshot_data(doc)) for doc in docs]

    @staticmethod
    def _snapshot_data(doc) -> dict[str, Any]:
        data = doc.to_dict()
        if data is None:
            raise ValueError(f"Firestore snapshot {doc.id} has no data")
        return data


def _project(data: dict[str, Any]) -> CardSnapshot:
    tz = get_app_timezone()
    return CardSnapshot(
        card_id=CardId(data["id"]),
        area_id=AreaId(data["area_id"]) if data["area_id"] else None,
        project_id=(
            ProjectId(data["project_id"]) if data.get("project_id") else None
        ),
        epic_id=EpicId(data["epic_id"]) if data.get("epic_id") else None,
        size=CardSize(data["size"]) if data["size"] else None,
        actual_time_minutes=data["actual_time"],
        created_at=Timestamp(data["created_at"].astimezone(tz)),
        entered_workflow_at=(
            Timestamp(data["entered_workflow_at"].astimezone(tz))
            if data.get("entered_workflow_at")
            else None
        ),
        completed_at=Timestamp(data["completed_at"].astimezone(tz)),
    )
