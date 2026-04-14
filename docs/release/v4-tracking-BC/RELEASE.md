# v4 Tracking BC — Release Notes

**Fecha:** 2026-04-14
**Scope:** Backend completo del bounded context `tracking` (sigma-core + sigma-rest).
**Depende de:** v3 — Metrics BC (tag v3-metrics-bc-backend).

---

## Bounded Context: tracking

Nuevo BC que gestiona sesiones de trabajo Pomodoro activas y el registro histórico de tiempo por card.

### Responsabilidades

- Estado mutable: `WorkSession` (sesion activa, una por space)
- Estado inmutable: `TrackingEntry` (entrada de tiempo registrada al cerrar sesion)
- Coordinacion inter-BC: evento `WorkSessionCompleted` → actualiza `work_log` en Card (task_management)

---

## Agregados nuevos

### WorkSession

Sesion activa de trabajo. Document_id = space_id en Firestore (uno por space).

State machine:

```
WORKING → complete_round() → BREAK (rounds pendientes) | COMPLETED (ultima ronda)
BREAK   → resume_from_break() → WORKING
WORKING | BREAK → stop(save=True)  → COMPLETED  (emite WorkSessionCompleted)
WORKING | BREAK → stop(save=False) → STOPPED    (descarta sin registrar)
```

Campos: `id`, `space_id`, `card_id`, `area_id?`, `project_id?`, `epic_id?`, `description`, `timer`, `completed_rounds`, `state`, `session_started_at`, `current_started_at`.

### TrackingEntry

Registro inmutable de tiempo trabajado. Se crea al cerrar una sesion con `save=True`.

Campos: `id`, `space_id`, `card_id`, `area_id?`, `project_id?`, `epic_id?`, `entry_type`, `description`, `minutes`, `logged_at`.

---

## Value Objects nuevos

- `Timer(technique, work_minutes, break_minutes, num_rounds)` — configuracion Pomodoro
- `TimerTechnique` — enum: `POMODORO`
- `WorkSessionId`, `TrackingEntryId` — UUIDs v4 tipados
- `EntryType` — enum: `WORK`

---

## Cambios en BCs existentes

### task_management — Card

- `work_log: list[WorkLogEntry]` — historial de sesiones de trabajo. Fuente de verdad de `actual_time` (invariante: `actual_time == sum(e.minutes for e in work_log)`).
- `timer_description: str | None` — descripcion capturada al iniciar el timer, consumida al detenerlo.
- `start_timer(now, description)` — acepta descripcion de lo que se va a trabajar.
- `stop_timer(now)` — crea `WorkLogEntry` con la descripcion almacenada; ya no muta `actual_time` directamente.
- `add_work_log(entry)` — añade entrada y actualiza `actual_time` en un solo punto (llamado desde `stop_timer` y desde `OnWorkSessionCompletedHandler`).

### metrics — MetricsBlock

- `actual_consumed_minutes: int` — suma de `actual_time_minutes` de cards completadas en el ciclo. Contrapartida real de `consumed_minutes` (estimado por size).

### shared_kernel — Events

- `WorkSessionCompleted(DomainEvent)` — emitido al completar una sesion (ultima ronda o stop con save). Campos: `space_id`, `card_id`, `area_id?`, `project_id?`, `epic_id?`, `description`, `minutes`.

---

## Event Handler inter-BC

### OnWorkSessionCompletedHandler

Suscrito a `WorkSessionCompleted`. Añade un `WorkLogEntry` al `work_log` de la card correspondiente. Si la card no existe, es no-op.

---

## REST API — Endpoints tracking

```
POST   /v1/spaces/{space_id}/tracking/sessions          → 201 WorkSessionResponse
GET    /v1/spaces/{space_id}/tracking/sessions/active   → 200 WorkSessionResponse | 204
POST   /v1/spaces/{space_id}/tracking/sessions/rounds   → 200 WorkSessionResponse
POST   /v1/spaces/{space_id}/tracking/sessions/resume   → 200 WorkSessionResponse
DELETE /v1/spaces/{space_id}/tracking/sessions?save=    → 204
```

### Cambios en endpoints existentes

```
POST /v1/cards/{card_id}/timer/start   — acepta body { "description": "" } (opcional)
```

---

## Colecciones Firestore nuevas

- `work_sessions` — sesiones activas; document_id = space_id (uno por space)
- `tracking_entries` — registros de tiempo; document_id = UUID

---

## Infraestructura

- `FirestoreWorkSessionRepository` — CRUD sobre `work_sessions`
- `FirestoreTrackingEntryRepository` — save + list_by_space sobre `tracking_entries`
- Mappers Firestore para `WorkSession` y `TrackingEntry`

---

## main.py — lifespan

Migrado de `@app.on_event("startup")` (deprecated) a `lifespan` context manager de FastAPI. El wiring de event handlers ocurre en startup garantizado por el context manager.

---

## Tests

| Suite | Tests |
|-------|-------|
| sigma-core unit | 605 |
| sigma-rest integration | 131 |
| **Total** | **736** |

Nuevos tests respecto a v3: +17 unit (use cases tracking), +3 unit (OnWorkSessionCompletedHandler), +11 REST integration (tracking endpoints), +2 unit (card work_log invariant), ajuste de 2 tests de mappers (size y timer_started_at: comportamiento tolerante a campos ausentes).

---

## Artefactos

- `openapi.json` — Schema OpenAPI 3.1 completo (67 paths)
