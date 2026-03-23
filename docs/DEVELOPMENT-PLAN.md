# SIGMA — Plan de desarrollo v1

**Versión:** 1.0
**Fecha:** 2026-03-21

---

## Roadmap de producto

El **Área** es el hilo conductor que conecta tablero, tiempo y métricas en todas las versiones.

| Versión | Nombre | Contenido |
|---|---|---|
| **V1** | Tablero | Kanban + Áreas + Prioridades |
| **V2** | Scheduling | Bloques de tiempo heredan color de Área. Cards pueden continuar entre bloques del mismo Área |
| **V3** | Sinergia | Integración tablero + scheduling. Una Card vive en ambas vistas de forma coherente |
| **V4** | Métricas | Análisis de productividad, tiempo por Área, velocidad de Cards, tendencias |

El plan de desarrollo de este documento cubre **V1 completa** (Fases 1–8).
V2 (Scheduling) está diseñada en `docs/design/UI-DESIGN.md § Vista de Scheduling`
y su arquitectura se añadirá a `sigma-core` como módulo `planning/` (ADR-006).

---

## Principios del plan

- **BDD-first**: el feature file es la especificación. Se escribe antes que el código de producción.
- **Ciclo por fase**: completar una fase antes de empezar la siguiente.
- **Pairing**: Alex escribe el código, Claude revisa y debate. Claude solo da la solución completa si se pide explícitamente.
- **Vertical slice**: cada fase entrega algo funcionando de extremo a extremo, no capas horizontales.

---

## Visión general de fases

```
Fase 1 → sigma-core: Value Objects + Aggregates (dominio puro)
Fase 2 → sigma-core: CardFilter + WipLimitRule
Fase 3 → sigma-core: Casos de uso + Ports + ErrorHandler
Fase 4 → sigma-rest: Infraestructura base + Repositorios Firestore
Fase 5 → sigma-rest: API REST completa
Fase 6 → sigma-mcp: Servidor MCP + Tools
Fase 7 → Seed script + smoke test
Fase 8 → sigma-web: PWA React
```

---

## Fase 1 — sigma-core: Value Objects y Aggregates

**Objetivo:** dominio puro funcionando con tests. Sin persistencia, sin frameworks.

### Setup inicial

```
packages/sigma-core/
  pyproject.toml         ← dependencias: behave, pytest
  behave.ini             ← configuración de paths y steps
  src/sigma_core/
    task_management/
      domain/
        __init__.py
        enums.py
        errors.py
        value_objects.py
        space.py
        card.py
        area.py
        project.py
        epic.py
  tests/
    features/domain/
    steps/domain/
    steps/common.py
```

### Orden de desarrollo dentro de la fase

**1.1 — Enums y errores** (sin tests, sin comportamiento)
- `enums.py`: `PreWorkflowStage`, `Priority`, `ProjectStatus`
- `errors.py`: jerarquía completa de `SigmaDomainError`

**1.2 — Value Objects** (feature: `value_objects.feature`)
Orden dentro del feature:
1. IDs (`CardId`, `SpaceId`, etc.) — más simples, base para todo lo demás
2. `CardTitle`, `SpaceName` — strings con invariantes
3. `Url` — validación de formato
4. `ChecklistItem` — inmutabilidad + métodos `complete/reopen`

Step definitions en `steps/domain/value_objects_steps.py`.

**1.3 — Space + WorkflowState** (feature: `space_workflow.feature`)
1. `WorkflowState` — entidad interna, sin comportamiento propio
2. `Space` — invariantes del workflow, `add_state`, `remove_state`, `is_valid_transition`

Step definitions en `steps/domain/space_workflow_steps.py`.

**1.4 — Card** (features: `card_stage.feature` + `card_content.feature`)
1. Construcción y discriminated union (`card_stage.feature`)
2. Operaciones sobre listas: labels, topics, urls, checklist, related cards (`card_content.feature`)

Step definitions en `steps/domain/card_steps.py`.

**1.5 — Area, Project, Epic**
Sin feature file dedicado — se cubren en `para_assignment.feature` (Fase 3).
Solo construcción y validaciones básicas de invariantes.

**Entregable de Fase 1:** suite behave verde para `tests/features/domain/`.

---

## Fase 2 — sigma-core: CardFilter y WipLimitRule

**Objetivo:** motor de predicados funcionando y testeado.

**Orden:**
1. Predicados por tipo: `StringPredicate`, `ListPredicate`, `NumericPredicate`, `DatePredicate`
2. `CardFilter.matches()` — evaluación en memoria
3. `WipLimitRule` — invariante `max_cards >= 1` + composición con `CardFilter`

Features: `card_filter.feature` + `wip_limit.feature`.
Step definitions en `steps/domain/card_filter_steps.py` y `steps/domain/wip_limit_steps.py`.

**Entregable de Fase 2:** `card_filter.feature` y `wip_limit.feature` en verde.

---

## Fase 3 — sigma-core: Ports, Casos de uso y ErrorHandler

**Objetivo:** lógica de aplicación completa. Los casos de uso se testean con repositorios en memoria (fakes).

### Setup

```
src/sigma_core/task_management/
  ports/
    card_repository.py
    space_repository.py
    area_repository.py
    project_repository.py
    epic_repository.py
  use_cases/
    space/
    card/
    area/
    project/
    epic/
  handlers.py
tests/
  fakes/                 ← repositorios en memoria para tests
    fake_card_repository.py
    fake_space_repository.py
    ...
  features/use_cases/
  steps/use_cases/
  steps/common.py        ← steps reutilizables (Given un Space existente, etc.)
```

### Fakes — repositorios en memoria

Los fakes implementan los Protocols con un dict en memoria.
Se construyen una vez en `steps/common.py` y se comparten entre escenarios via `context`.

### Orden de desarrollo dentro de la fase

**3.1 — Ports** (solo interfaces Protocol, sin implementación)

**3.2 — ErrorHandler**
- `ErrorResult` dataclass
- `handle_domain_error()` con match/case sobre toda la jerarquía

**3.3 — Casos de uso de Space**
Feature: no existe feature dedicado para Space use cases — se cubren indirectamente en los Background de los otros features.
Orden: `CreateSpace` → `AddWorkflowState` → `RemoveWorkflowState`

**3.4 — Casos de uso de Card** (features: `create_card.feature`, `move_card.feature`, `promote_demote.feature`)
Orden crítico — cada uno depende del anterior:
1. `CreateCard` — el más simple, solo necesita `CardRepository` y `SpaceRepository`
2. `PromoteToWorkflow` — necesita validar WIP limits
3. `MoveWithinWorkflow` — más complejo: transición + WIP limits con filtro
4. `DemoteToPreWorkflow` — simple
5. `ArchiveCard` — trivial una vez que existe `MoveWithinWorkflow`
6. `DeleteCard` — trivial

**3.5 — Casos de uso de Area, Project, Epic** (feature: `para_assignment.feature`)
Orden: `CreateArea` → `CreateProject` → `CreateEpic` → `AssignProject` (infiere Area) → `DeleteArea` (cascada)

**3.6 — Casos de uso de consulta** (Queries)
`GetCard`, `GetCardsBySpace`, `GetCardsByWorkflowState`, etc.
Sin feature file dedicado — se usan en los Background de otros tests.

**Entregable de Fase 3:** todos los feature files de `use_cases/` en verde con fakes.

---

## Fase 4 — sigma-rest: Infraestructura base y Repositorios Firestore

**Objetivo:** adaptadores de salida funcionando contra Firestore real (emulador local).

### Setup

```
packages/sigma-rest/
  pyproject.toml
  .env.example
  src/sigma_rest/
    config/
      settings.py        ← pydantic-settings
    adapters/
      firestore_card_repository.py
      firestore_space_repository.py
      firestore_area_repository.py
      firestore_project_repository.py
      firestore_epic_repository.py
    schemas/             ← vacío por ahora
    mappers/             ← vacío por ahora
    api/                 ← vacío por ahora
  tests/
    integration/
      test_card_repository.py
      test_space_repository.py
      ...
```

### Orden de desarrollo

**4.1 — Settings y conexión Firestore**
`FirestoreSettings` con `pydantic-settings`. Test de conexión al emulador.

**4.2 — Repositorios** (tests de integración con pytest + emulador Firestore)
Orden por dependencia:
1. `FirestoreSpaceRepository` — más simple, no depende de otros
2. `FirestoreAreaRepository` + `FirestoreProjectRepository` + `FirestoreEpicRepository`
3. `FirestoreCardRepository` — el más complejo: fanout atómico en MoveCard, índices

Cada repositorio se testea con:
- `save` + `get_by_id` (happy path)
- `get_by_id` de ID inexistente → `None`
- Transacción atómica en operaciones multi-documento (MoveCard)

**Entregable de Fase 4:** tests de integración verdes contra emulador Firestore local.

---

## Fase 5 — sigma-rest: API REST completa

**Objetivo:** API funcionando end-to-end (PWA puede consumirla).

### Setup

```
src/sigma_rest/
  schemas/
    space_schemas.py
    card_schemas.py
    area_schemas.py
    project_schemas.py
    epic_schemas.py
    error_schemas.py
  mappers/
    space_mappers.py
    card_mappers.py
    area_mappers.py
    project_mappers.py
    epic_mappers.py
  api/
    routers/
      spaces.py
      cards.py
      areas.py
      projects.py
      epics.py
    dependencies.py      ← FastAPI Depends — construye casos de uso con repos reales
    error_handlers.py    ← consume ErrorResult, devuelve HTTPException
    main.py
```

### Orden de desarrollo

**5.1 — Error handlers REST**
Mapeo `ErrorResult → HTTPException` con body JSON estructurado según catálogo.

**5.2 — Schemas y mappers** (sin tests propios — se verifican en los tests de endpoint)

**5.3 — Endpoints** por recurso, siguiendo el catálogo `API-REST-CATALOGUE.md`:
1. `GET /spaces` + `POST /spaces` + workflow states
2. `GET /spaces/{id}/board` — vista del tablero
3. `POST /spaces/{id}/cards` + `GET /cards/{id}` + `PATCH /cards/{id}`
4. Movimientos: `PATCH /cards/{id}/move` + `promote` + `demote` + `archive`
5. Contenido: labels, topics, urls, checklist, related
6. Areas + Projects + Epics

Tests: pytest con cliente HTTP de FastAPI (`TestClient`) contra repositorios fake o emulador.

**Entregable de Fase 5:** API REST completa y documentada (OpenAPI auto-generado por FastAPI).

---

## Fase 6 — sigma-mcp: Servidor MCP y Tools

**Objetivo:** Claude puede gestionar SIGMA directamente desde una conversación.

### Setup

```
packages/sigma-mcp/
  pyproject.toml
  .env.example
  src/sigma_mcp/
    schemas/
    mappers/
    adapters/            ← mismos repositorios Firestore que sigma-rest
    tools/
      space_tools.py
      card_tools.py
      area_tools.py
      epic_tools.py
    error_handlers.py    ← consume ErrorResult, devuelve objeto estructurado MCP
    server.py
```

### Orden de desarrollo

**6.1 — Reutilización de adaptadores Firestore**
Los repositorios Firestore se comparten entre `sigma-rest` y `sigma-mcp`
extrayéndolos a un paquete interno o duplicando (decisión a tomar en el momento).

**6.2 — Error handler MCP**
Errores de dominio como datos estructurados en la respuesta de la tool
(Claude puede razonar sobre ellos y proponer alternativas).

**6.3 — Tools** siguiendo el catálogo `MCP-TOOLS-CATALOGUE.md`:
1. `list_spaces` + `get_board` — consultas de lectura, las más usadas
2. `create_card` + `move_card` + `promote_card_to_workflow`
3. Resto de tools de ciclo de vida y contenido
4. Tools de Area, Project, Epic

**Entregable de Fase 6:** Claude puede crear, mover y consultar Cards desde una conversación.

---

## Fase 7 — Seed script y smoke test

**Objetivo:** la app arranca con un estado útil y verificable.

```
packages/sigma-rest/
  scripts/
    seed.py              ← crea My Personal Space con datos de ejemplo
```

**Contenido del seed:**

```
Space: "My Personal Space"
  Workflow: TO DO (Start, wip_limit=3) → WIP → DONE (End)

Area:    "Personal"
Project: "Onboarding SIGMA"  (area: Personal)
Epic:    "Primeros pasos"    (space: My Personal Space)

Cards de ejemplo:
  [INBOX]      "Explorar SIGMA — empieza aquí"
               labels: ["#onboarding"], topics: ["SIGMA"]
               checklist: ["Abre una card", "Muévela a TO DO", "Complétala"]

  [REFINEMENT] "Define tu primer proyecto"
               description: "Crea un Area y un Project que refleje tu trabajo"

  [BACKLOG]    "Configura tu workflow ideal"
               description: "Edita los estados del Space según tu metodología"
               priority: medium

  [TO DO]      "Completar esta tarea de ejemplo"
               epic: "Primeros pasos"
               project: "Onboarding SIGMA"
               priority: high
               due_date: <hoy + 3 días>
```

El seed es idempotente — si el Space ya existe, no lo recrea.

**Smoke test:** script que verifica que el seed se ejecutó correctamente
consultando los datos a través del repositorio.

**Entregable de Fase 7:** `uv run python scripts/seed.py` deja la app en estado usable.

---

## Fase 8 — sigma-web: PWA React

**Objetivo:** interfaz web funcional que consume la API REST.

El orden de desarrollo de la UI sigue la prioridad de uso:

1. **Autenticación** — Firebase Auth + Google OAuth
2. **Vista de tablero** — columnas pre-workflow + workflow, cards compactas
3. **Panel de detalle** — todas las propiedades de la Card editables
4. **Movimiento de Cards** — drag & drop + validación WIP limit en cliente
5. **Barra de filtros** — CardFilter aplicado en cliente y servidor
6. **Vista PARA** — Areas → Proyectos → Cards
7. **Vista Epics** — agrupación y progreso
8. **Configuración de Space** — edición del workflow

**Entregable de Fase 8:** PWA desplegada en Firebase Hosting, accesible desde móvil y desktop.

---

## Resumen de entregables por fase

| Fase | Entregable | Verificación |
|---|---|---|
| 1 | Dominio: VOs + Aggregates | `behave tests/features/domain/` verde |
| 2 | Dominio: CardFilter + WipLimitRule | `behave tests/features/domain/` verde |
| 3 | Use cases + Ports + ErrorHandler | `behave tests/features/use_cases/` verde |
| 4 | Repositorios Firestore | `pytest tests/integration/` verde |
| 5 | API REST completa | `pytest tests/api/` verde + OpenAPI disponible |
| 6 | Servidor MCP | Claude gestiona Cards en conversación |
| 7 | Seed + smoke test | `seed.py` ejecuta sin errores |
| 8 | PWA React | Accesible en Firebase Hosting |

---

## Notas de pairing

- Cada fase arranca revisando el feature file correspondiente antes de escribir código
- Si un escenario no está claro, se debate antes de implementar — no después
- El orden dentro de cada fase es una guía, no una ley — si al implementar algo se descubre una dependencia distinta, se ajusta
- Los ADRs se actualizan si durante la implementación aparece una decisión significativa no prevista
