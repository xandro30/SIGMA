"""Conftest de los tests de integración contra Firestore.

Requiere el emulator oficial de Firestore corriendo (``docker-compose up
firestore`` arranca el servicio definido en la raíz del repo). Si el
emulator no está disponible, todos los tests de esta carpeta se skipean
con un mensaje claro, en lugar de fallar ruidosamente con
``DefaultCredentialsError`` al intentar autenticar contra GCP real.
"""
from __future__ import annotations

import os
import socket

import httpx
import pytest
import pytest_asyncio

from sigma_core.task_management.infrastructure.firestore.client import (
    get_firestore_client,
)
from sigma_core.task_management.infrastructure.firestore.config import (
    FirestoreConfig,
)


DEFAULT_EMULATOR_HOST = "localhost:8080"
TEST_PROJECT_ID = "sigma-test"


def _emulator_host() -> str:
    return os.environ.get("FIRESTORE_EMULATOR_HOST", DEFAULT_EMULATOR_HOST)


def _emulator_reachable(host: str, timeout: float = 0.5) -> bool:
    """``True`` si hay un socket TCP escuchando en ``host:port``.

    No verifica que el servicio sea realmente el emulator — solo que algo
    responde. Es suficiente para decidir skip vs. run: si hay otra cosa
    escuchando en ese puerto los tests fallarán, pero con un mensaje del
    emulator, no con ``DefaultCredentialsError``.
    """
    try:
        hostname, port_str = host.split(":")
        with socket.create_connection((hostname, int(port_str)), timeout=timeout):
            return True
    except (OSError, ValueError):
        return False


def pytest_collection_modifyitems(config, items):
    """Skip automático de toda la suite si el emulator no está arrancado.

    Permite correr ``uv run pytest`` sin dependencias externas: los tests
    unit corren normal, los de integración se skipean con un mensaje que
    explica cómo arrancar el emulator.
    """
    host = _emulator_host()
    if _emulator_reachable(host):
        # Asegura que el cliente use el emulator aunque el usuario no haya
        # exportado la env var (``FirestoreConfig.is_emulator`` depende de
        # ella — sin esto el cliente caería a Application Default Credentials).
        os.environ.setdefault("FIRESTORE_EMULATOR_HOST", host)
        return

    skip_no_emulator = pytest.mark.skip(
        reason=(
            f"Firestore emulator no alcanzable en {host}. "
            "Arráncalo con `docker-compose up firestore` desde la raíz del "
            "repo (expone localhost:8080) o exporta FIRESTORE_EMULATOR_HOST "
            "apuntando a un emulator alternativo."
        )
    )
    integration_marker = os.sep + "tests" + os.sep + "integration" + os.sep
    for item in items:
        if integration_marker in str(item.fspath):
            item.add_marker(skip_no_emulator)


@pytest.fixture(scope="session")
def firestore_config():
    return FirestoreConfig(project_id=TEST_PROJECT_ID)


@pytest_asyncio.fixture
async def firestore_client(firestore_config):
    client = get_firestore_client(firestore_config)
    yield client
    client.close()


@pytest_asyncio.fixture(autouse=True)
async def cleanup():
    """Limpia TODOS los documentos del emulator entre tests.

    La URL se construye a partir de ``FIRESTORE_EMULATOR_HOST`` y del
    ``TEST_PROJECT_ID`` para mantener ambos en el mismo sitio. Si la llamada
    falla (emulator caído durante el teardown, por ejemplo), el fallo se
    ignora — el pytest report de ese test ya mostrará la causa raíz, no
    queremos ensuciar la salida con un error de cleanup secundario.
    """
    yield
    host = _emulator_host()
    url = (
        f"http://{host}/emulator/v1/projects/{TEST_PROJECT_ID}"
        "/databases/(default)/documents"
    )
    try:
        async with httpx.AsyncClient() as client:
            await client.delete(url)
    except httpx.HTTPError:
        pass
