import pytest
import pytest_asyncio
import httpx

from sigma_core.task_management.infrastructure.firestore.config import FirestoreConfig
from sigma_core.task_management.infrastructure.firestore.client import get_firestore_client


@pytest.fixture(scope="session")
def firestore_config():
    return FirestoreConfig(project_id="sigma-test")


@pytest_asyncio.fixture
async def firestore_client(firestore_config):
    client = get_firestore_client(firestore_config)
    yield client
    client.close()


@pytest_asyncio.fixture(autouse=True)
async def cleanup():
    yield
    async with httpx.AsyncClient() as client:
        await client.delete(
            "http://localhost:8080/emulator/v1/projects/sigma-test/databases/(default)/documents"
        )