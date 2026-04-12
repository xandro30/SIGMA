"""Configuración del adaptador HTTP.

Leer de env vars es el único mecanismo: los valores aquí afectan al runtime
del servidor (orígenes CORS, etc.) y no pertenecen al dominio, así que no
viven en ``sigma_core.shared_kernel.config``.
"""
from __future__ import annotations

import os


DEFAULT_CORS_ORIGINS = "http://localhost:5173"


def get_cors_origins() -> list[str]:
    """Lista de orígenes permitidos por CORS.

    Se lee de ``SIGMA_CORS_ORIGINS`` como lista separada por comas. Valor por
    defecto: ``http://localhost:5173`` (frontend local de desarrollo).
    Los espacios alrededor de cada origen se ignoran; entradas vacías se
    descartan.
    """
    raw = os.environ.get("SIGMA_CORS_ORIGINS", DEFAULT_CORS_ORIGINS)
    origins = [origin.strip() for origin in raw.split(",")]
    return [o for o in origins if o]
