from __future__ import annotations

from typing import Any

from google.cloud.firestore import AsyncClient

from sigma_core.shared_kernel.value_objects import SpaceId


class FirestoreMetricsSpaceReader:
    COLLECTION = "spaces"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def get_size_mapping(
        self, space_id: SpaceId
    ) -> dict[str, int] | None:
        doc = await (
            self._client.collection(self.COLLECTION)
            .document(space_id.value)
            .get()
        )
        if not doc.exists:
            return None
        data = doc.to_dict()
        if data is None:
            return None
        return data.get("size_mapping")
