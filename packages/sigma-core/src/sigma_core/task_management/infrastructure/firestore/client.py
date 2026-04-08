import os
from unittest.mock import Mock

import firebase_admin
from firebase_admin import credentials
import google.auth.credentials
from google.cloud.firestore import AsyncClient

from sigma_core.task_management.infrastructure.firestore.config import FirestoreConfig


def get_firestore_client(config: FirestoreConfig) -> AsyncClient:
    if config.emulator_host:
        os.environ["FIRESTORE_EMULATOR_HOST"] = config.emulator_host

    if not firebase_admin._apps:
        if config.is_emulator:
            firebase_admin.initialize_app(
                options={"projectId": config.project_id},
            )
        else:
            firebase_admin.initialize_app(
                credential=credentials.ApplicationDefault(),
                options={"projectId": config.project_id},
            )

    if config.is_emulator:
        return AsyncClient(
            project=config.project_id,
            credentials=Mock(spec=google.auth.credentials.Credentials),
        )

    return AsyncClient(project=config.project_id)