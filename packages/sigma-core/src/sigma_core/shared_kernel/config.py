"""Configuración compartida entre bounded contexts.

Solo valores que son verdaderamente globales al dominio (zona horaria de
aplicación, por ejemplo). Cualquier cosa específica de un BC vive en el
módulo ``config`` de ese BC.
"""
from __future__ import annotations

import os
from zoneinfo import ZoneInfo


DEFAULT_APP_TIMEZONE = "Europe/Madrid"


def get_app_timezone() -> ZoneInfo:
    """Zona horaria del dominio.

    Se lee de ``SIGMA_APP_TZ`` en cada llamada; el módulo ``zoneinfo`` tiene
    su propio cache interno, por lo que repetir la lectura es barato y permite
    que los tests alternen la TZ con ``monkeypatch.setenv`` sin gimnasia.

    El default es ``Europe/Madrid``: deliberado, no accidental, ya que SIGMA
    nació como herramienta personal de un usuario en esa zona horaria.
    """
    tz_name = os.environ.get("SIGMA_APP_TZ", DEFAULT_APP_TIMEZONE)
    return ZoneInfo(tz_name)
