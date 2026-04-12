"""Shared kernel de SIGMA.

Contiene los conceptos primitivos que múltiples bounded contexts comparten
(identificadores, medidas, base de errores, envoltorios de aplicación). Un
símbolo vive aquí cuando:

- Lo usan dos o más BCs.
- No tiene reglas de negocio específicas de un solo BC.
- Su semántica no depende del agregado concreto que lo contenga.

Los símbolos específicos de un BC permanecen en ``<bc>.domain``. El shared
kernel NO tiene conocimiento de ningún BC concreto — solo define tipos base.

Guía de importación:
    from sigma_core.shared_kernel.value_objects import SpaceId, Minutes
    from sigma_core.shared_kernel.enums import CardSize
    from sigma_core.shared_kernel.errors import SigmaDomainError
    from sigma_core.shared_kernel.error_result import ErrorResult
"""
