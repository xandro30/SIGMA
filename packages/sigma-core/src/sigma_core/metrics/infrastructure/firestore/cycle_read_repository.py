from __future__ import annotations

from typing import Any

from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.metrics.domain.value_objects import CycleView
from sigma_core.planning.domain.value_objects import CycleId, DateRange
from sigma_core.shared_kernel.value_objects import AreaId, SpaceId


class FirestoreMetricsCycleReader:
    COLLECTION = "cycles"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get_by_id(self, cycle_id: CycleId) -> CycleView | None:
        doc = await (
            self._client.collection(self.COLLECTION)
            .document(cycle_id.value)
            .get()
        )
        if not doc.exists:
            return None
        return _cycle_view_from_dict(_snapshot_data(doc))

    async def get_active_by_space(
        self, space_id: SpaceId
    ) -> CycleView | None:
        docs = await (
            self._client.collection(self.COLLECTION)
            .where(filter=FieldFilter("space_id", "==", space_id.value))
            .where(filter=FieldFilter("state", "==", "active"))
            .limit(1)
            .get()
        )
        if not docs:
            return None
        return _cycle_view_from_dict(_snapshot_data(docs[0]))


def _snapshot_data(doc) -> dict[str, Any]:
    data = doc.to_dict()
    if data is None:
        raise ValueError(f"Firestore snapshot {doc.id} has no data")
    return data


def _cycle_view_from_dict(data: dict[str, Any]) -> CycleView:
    from datetime import date

    return CycleView(
        id=CycleId(data["id"]),
        space_id=SpaceId(data["space_id"]),
        date_range=DateRange(
            start=date.fromisoformat(data["date_range"]["start"]),
            end=date.fromisoformat(data["date_range"]["end"]),
        ),
        area_budgets={
            AreaId(aid): minutes
            for aid, minutes in data["area_budgets"].items()
        },
        buffer_percentage=data["buffer_percentage"],
        state=data["state"],
    )
