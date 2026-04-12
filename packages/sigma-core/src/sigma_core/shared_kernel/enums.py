from __future__ import annotations

from enum import Enum


class CardSize(str, Enum):
    """Talla de una Card, compartida entre task_management (atributo de
    Card) y planning (conversión a minutos a través de SizeMapping)."""

    XXS = "xxs"
    XS = "xs"
    S = "s"
    M = "m"
    L = "l"
    XL = "xl"
    XXL = "xxl"
