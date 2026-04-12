"""Límites compartidos de longitudes de campos en los schemas Pydantic.

Valores generosos pero finitos: el objetivo es rechazar payloads
abusivamente grandes en el borde HTTP sin entorpecer usos legítimos. Los
invariantes de negocio más estrictos (longitud exacta de UUID, reglas de
titulado, etc.) viven en los value objects del dominio.
"""
from __future__ import annotations

# Strings cortos (nombres de entidades)
MIN_NAME_LENGTH = 1
MAX_NAME_LENGTH = 200

# Notas libres
MAX_NOTES_LENGTH = 2000

# UUID canónico en forma string
UUID_STRING_LENGTH = 36
