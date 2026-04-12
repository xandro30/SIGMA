from __future__ import annotations

from typing import Any

from google.cloud.firestore import AsyncClient

from sigma_core.planning.domain.read_models.space_view import SpaceView
from sigma_core.shared_kernel.value_objects import SizeMapping, SpaceId


class FirestoreSpaceReader:
    """Planning-owned read projection over the `spaces` collection.

    Projects directly to `SpaceView` without reconstructing the Space
    aggregate, keeping the planning BC decoupled from task_management
    domain types.
    """

    COLLECTION = "spaces"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get_by_id(self, space_id: SpaceId) -> SpaceView | None:
        doc = await (
            self._client.collection(self.COLLECTION).document(space_id.value).get()
        )
        if not doc.exists:
            return None
        return _space_view_from_dict(_snapshot_data(doc))


def _snapshot_data(doc) -> dict[str, Any]:
    data = doc.to_dict()
    if data is None:
        raise ValueError(f"Firestore snapshot {doc.id} has no data")
    return data


def _space_view_from_dict(data: dict[str, Any]) -> SpaceView:
    raw_mapping = data["size_mapping"]
    size_mapping = (
        SizeMapping.from_primitive(raw_mapping) if raw_mapping is not None else None
    )
    return SpaceView(
        id=SpaceId(data["id"]),
        size_mapping=size_mapping,
    )
