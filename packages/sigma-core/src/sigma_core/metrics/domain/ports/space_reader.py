from __future__ import annotations

from typing import Protocol

from sigma_core.shared_kernel.value_objects import SpaceId


class MetricsSpaceReader(Protocol):
    async def get_size_mapping(
        self, space_id: SpaceId
    ) -> dict[str, int] | None: ...
