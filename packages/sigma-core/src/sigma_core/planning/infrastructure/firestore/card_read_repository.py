from __future__ import annotations

from datetime import datetime, time
from typing import Any

from google.cloud.firestore import AsyncClient
from google.cloud.firestore_v1.base_query import FieldFilter

from sigma_core.planning.domain.read_models.card_view import CardView
from sigma_core.planning.domain.value_objects import DateRange
from sigma_core.shared_kernel.config import get_app_timezone
from sigma_core.shared_kernel.enums import CardSize
from sigma_core.shared_kernel.value_objects import (
    AreaId,
    CardId,
    Minutes,
    SpaceId,
    Timestamp,
)


class FirestoreCardReader:
    """Planning-owned read projection over the `cards` collection.

    Reads the persistence data shared with task_management but never
    reconstructs the `Card` aggregate — projects directly to `CardView`
    so the planning BC stays decoupled from task_management domain types.

    Composite index required for `list_completed_in_range`:
        cards: space_id ASC, completed_at ASC
    """

    COLLECTION = "cards"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get_by_id(self, card_id: CardId) -> CardView | None:
        doc = await (
            self._client.collection(self.COLLECTION).document(card_id.value).get()
        )
        if not doc.exists:
            return None
        return _card_view_from_dict(_snapshot_data(doc))

    async def list_completed_in_range(
        self, space_id: SpaceId, date_range: DateRange
    ) -> list[CardView]:
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
        return [_card_view_from_dict(_snapshot_data(doc)) for doc in docs]


def _snapshot_data(doc) -> dict[str, Any]:
    data = doc.to_dict()
    if data is None:
        raise ValueError(f"Firestore snapshot {doc.id} has no data")
    return data


def _card_view_from_dict(data: dict[str, Any]) -> CardView:
    raw_completed_at = data["completed_at"]
    completed_at = (
        Timestamp(raw_completed_at.astimezone(get_app_timezone()))
        if raw_completed_at is not None
        else None
    )
    raw_area_id = data["area_id"]
    raw_size = data["size"]
    return CardView(
        id=CardId(data["id"]),
        space_id=SpaceId(data["space_id"]),
        area_id=AreaId(raw_area_id) if raw_area_id is not None else None,
        size=CardSize(raw_size) if raw_size is not None else None,
        actual_time=Minutes(data["actual_time"]),
        completed_at=completed_at,
    )
