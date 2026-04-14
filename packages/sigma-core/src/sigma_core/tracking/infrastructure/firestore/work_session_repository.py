"""Firestore repository para WorkSession."""
from __future__ import annotations

from google.cloud.firestore import AsyncClient

from sigma_core.shared_kernel.value_objects import SpaceId
from sigma_core.tracking.domain.aggregates.work_session import WorkSession
from sigma_core.tracking.infrastructure.firestore.mappers import (
    snapshot_data,
    work_session_from_dict,
    work_session_to_dict,
)


class FirestoreWorkSessionRepository:
    """Un documento por space — document_id = space_id."""

    COLLECTION = "work_sessions"

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    def _ref(self, space_id: str):
        return self._client.collection(self.COLLECTION).document(space_id)

    async def save(self, session: WorkSession) -> None:
        await self._ref(session.space_id.value).set(work_session_to_dict(session))

    async def get_by_space(self, space_id: SpaceId) -> WorkSession | None:
        doc = await self._ref(space_id.value).get()
        if not doc.exists:
            return None
        return work_session_from_dict(snapshot_data(doc))

    async def delete(self, space_id: SpaceId) -> None:
        await self._ref(space_id.value).delete()
