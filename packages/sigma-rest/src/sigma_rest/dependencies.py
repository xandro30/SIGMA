from functools import lru_cache
from google.cloud.firestore import AsyncClient

from sigma_core.task_management.infrastructure.firestore.config import FirestoreConfig
from sigma_core.task_management.infrastructure.firestore.client import get_firestore_client
from sigma_core.task_management.infrastructure.firestore.card_repository import FirestoreCardRepository
from sigma_core.task_management.infrastructure.firestore.space_repository import FirestoreSpaceRepository
from sigma_core.task_management.infrastructure.firestore.area_repository import FirestoreAreaRepository
from sigma_core.task_management.infrastructure.firestore.project_repository import FirestoreProjectRepository
from sigma_core.task_management.infrastructure.firestore.epic_repository import FirestoreEpicRepository


@lru_cache
def get_config() -> FirestoreConfig:
    return FirestoreConfig()


@lru_cache
def get_client() -> AsyncClient:
    return get_firestore_client(get_config())


def get_card_repo() -> FirestoreCardRepository:
    return FirestoreCardRepository(get_client())


def get_space_repo() -> FirestoreSpaceRepository:
    return FirestoreSpaceRepository(get_client())


def get_area_repo() -> FirestoreAreaRepository:
    return FirestoreAreaRepository(get_client())


def get_project_repo() -> FirestoreProjectRepository:
    return FirestoreProjectRepository(get_client())


def get_epic_repo() -> FirestoreEpicRepository:
    return FirestoreEpicRepository(get_client())