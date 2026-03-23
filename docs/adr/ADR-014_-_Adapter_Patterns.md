# ADR-014: Patrones de adaptador — DTOs, Mappers, Error Handling e Inyección de dependencias

**Estado:** Aceptado
**Fecha:** 2026-03-21

## Contexto

Los adaptadores `sigma-rest` y `sigma-mcp` necesitan comunicarse con
`sigma-core` sin acoplar el dominio a sus protocolos. Se necesita definir:
cómo se serializan los datos, cómo se traducen los errores de dominio, y
cómo los casos de uso reciben sus dependencias.

## Decisión

### 1. DTOs y Mappers por adaptador

El dominio devuelve objetos de dominio puros (`Card`, `Space`, etc.).
Cada adaptador es responsable de su propio contrato de serialización.

```
sigma-rest/
  schemas/     ← Pydantic models para request/response HTTP
  mappers/     ← Card → CardResponse, CreateCardRequest → CreateCard(cmd)

sigma-mcp/
  schemas/     ← estructuras de datos para tools MCP
  mappers/     ← equivalente para el protocolo MCP
```

El dominio no conoce ni Pydantic ni JSON. Nunca hereda de `BaseModel`.

### 2. Error Handler en sigma-core

`sigma-core` expone un handler agnóstico al protocolo que mapea la
jerarquía `SigmaDomainError` a una estructura común `ErrorResult`:

```python
# sigma-core/handlers.py

@dataclass(frozen=True)
class ErrorResult:
    code: str     # identificador de máquina: "wip_limit_exceeded"
    message: str  # mensaje legible
    detail: dict  # datos estructurados del error

def handle_domain_error(exc: SigmaDomainError) -> ErrorResult: ...
```

Cada adaptador consume `ErrorResult` y lo traduce a su protocolo:
- `sigma-rest` → `HTTPException` con código y body JSON estructurado
- `sigma-mcp` → objeto estructurado en la respuesta de la tool
- `sigma-cli` (futura) → mensaje formateado + exit code controlado

### 3. Inyección de dependencias — constructor injection

Los casos de uso reciben sus repositorios en el constructor:

```python
class MoveWithinWorkflow:
    def __init__(
        self,
        card_repo: CardRepository,
        space_repo: SpaceRepository,
    ) -> None:
        self._card_repo = card_repo
        self._space_repo = space_repo

    async def execute(self, cmd: MoveWithinWorkflowCommand) -> None: ...
```

Los adaptadores construyen los casos de uso en el arranque y los
inyectan vía FastAPI `Depends` o equivalente MCP.

## Razonamiento

**DTOs separados:** el dominio no debe acoplarse al contrato de ningún
protocolo. REST y MCP tienen estructuras distintas — un único modelo
compartido obligaría a compromisos en ambos sentidos. Mappers explícitos
hacen visible la conversión y son fáciles de testear de forma aislada.

**ErrorHandler en core:** los errores de dominio necesitan ser
interpretados por todos los adaptadores de forma consistente. Centralizar
el mapeo en `sigma-core` evita que cada adaptador reimplemente la misma
lógica de interpretación. El `ErrorResult` es agnóstico al protocolo —
cada adaptador lo traduce a su forma natural.

**Constructor injection:** hace explícitas las dependencias de cada caso
de uso, facilita el testing (se pasan mocks en el constructor) y es
la forma más legible — las dependencias son visibles en la firma del
constructor sin necesidad de frameworks de DI.

## Alternativas consideradas

- **Dominio con Pydantic (BaseModel)**: acopla el dominio a la librería
  de serialización. Un cambio en Pydantic afecta al núcleo del sistema.
  Descartado — viola DIP.
- **Error handling por endpoint**: cada endpoint/tool maneja sus propios
  errores. Produce duplicación y riesgo de inconsistencia entre adaptadores.
  Descartado.
- **Inyección por parámetro en execute()**: las dependencias no son
  visibles en la construcción del objeto. Más difícil de razonar sobre
  el grafo de dependencias. Descartado.

## Consecuencias

- `sigma-core` no tiene dependencias de FastAPI, Pydantic ni MCP
- Cada adaptador mantiene sus propios schemas y mappers
- `sigma-core/handlers.py` es el único lugar donde vive el mapeo
  `SigmaDomainError → ErrorResult`
- Los casos de uso son testeables pasando mocks en el constructor
  sin necesidad de frameworks de DI ni monkey-patching
- El seed script construye casos de uso directamente con repositorios
  Firestore reales
