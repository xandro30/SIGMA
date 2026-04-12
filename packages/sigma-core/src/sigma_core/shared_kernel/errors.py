class SigmaDomainError(Exception):
    """Base de la jerarquía de errores de dominio.

    Todas las excepciones de negocio de los bounded contexts extienden de
    esta clase, lo que permite a los adaptadores distinguir errores de
    dominio de errores técnicos con un único ``isinstance`` check.
    """
