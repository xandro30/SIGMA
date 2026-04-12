from sigma_core.planning.domain.read_models.space_view import SpaceView
from sigma_core.shared_kernel.value_objects import SpaceId


class FakeSpaceReader:
    """In-memory fake for the planning.SpaceReader port."""

    def __init__(self) -> None:
        self._store: dict[str, SpaceView] = {}

    def add(self, space: SpaceView) -> None:
        self._store[space.id.value] = space

    async def get_by_id(self, space_id: SpaceId) -> SpaceView | None:
        return self._store.get(space_id.value)
