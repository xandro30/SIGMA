from dataclasses import dataclass


@dataclass(frozen=True)
class ErrorResult:
    """Envoltura genérica de errores de dominio hacia los adaptadores.

    Se comparte entre bounded contexts para mantener una única forma en
    los exception handlers del adaptador HTTP (FastAPI) y evitar que
    cada BC duplique el mismo dataclass.
    """

    code: str
    message: str
    detail: dict
    status_code: int
