# v2 Planning BC — Release Notes

**Fecha:** 2026-04-12
**Scope:** Backend completo del bounded context `planning` (sigma-core + sigma-rest).
**Depende de:** Plan 1 — Estimation (cerrado previamente).

---

## Aggregates

### Cycle
Periodo planificable con un unico ciclo activo por Space. Asociacion Card-Cycle implicita por `completed_at` dentro del rango (sin FK).

- CRUD completo (create, get, delete)
- Lifecycle: draft -> active -> closed
- Area budgets: `area_id -> Minutes` por ciclo
- Buffer configurable: 0-100% (default interno del aggregate)

### Day + DayTemplate
Day es un dia concreto con TimeBlocks. DayTemplate es una plantilla reutilizable (fork, no link).

- DayId determinista: `uuid5(namespace, f"{space_id}:{date}")` — race-safe en concurrencia
- TimeBlocks con validacion de overlap, wraparound y max 48 bloques
- Apply template: materializa bloques con `replace_existing` opcional
- UNSET sentinel para distinguir "no tocar" de "poner a None" en updates

### Week + WeekTemplate
Week es un contenedor semanal. WeekTemplate define slots (lunes-domingo) referenciando DayTemplates.

- WeekId determinista: `uuid5(namespace, f"{space_id}:{week_start}")`
- Invariante: `week_start` debe ser lunes
- Lazy creation: crear Week no materializa los 7 Days
- Apply template: pre-resolucion de todos los DayTemplates (fail fast), materializacion atomica
- Delete cascada: borra Week + 7 Days del rango
- Cross-space validation: WeekTemplate y DayTemplates referenciados deben pertenecer al mismo Space

---

## Queries (read models)

### GetSpaceCapacity
Consumo vs presupuesto por Area dentro del ciclo activo.

- Usa `CardReader.list_completed_in_range` (filtra por `completed_at`, no por workflow_state_id)
- Projections: `CardView` y `SpaceView` (DTOs de planning, no aggregates de task_management)

### GetCardEta
Fecha estimada de completado de una Card.

- Calculo on-demand, sin persistir
- Usa `size_mapping` + daily capacity (budget/5) + buffer del ciclo
- Dias laborables (lunes-viernes)

---

## Shared Kernel

Nuevo paquete `sigma_core.shared_kernel` con tipos compartidos entre BCs:

| Modulo | Contenido |
|--------|-----------|
| `value_objects.py` | SpaceId, AreaId, CardId, Minutes, Timestamp, SizeMapping |
| `enums.py` | CardSize |
| `errors.py` | SigmaDomainError (base) |
| `error_result.py` | ErrorResult (dataclass generico para handlers) |
| `config.py` | `get_app_timezone()` (env var `SIGMA_APP_TZ`, default Europe/Madrid) |

**Resultado:** planning tiene 0 imports desde task_management.

---

## REST API — Planning endpoints

Todos los endpoints de planning estan nested bajo `/v1/spaces/{space_id}/...`:

### Cycles (`/v1/spaces/{space_id}/cycles`)
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/cycles` | Crear ciclo (draft) |
| GET | `/cycles/active` | Ciclo activo del Space |
| GET | `/cycles/{id}` | Detalle de ciclo |
| POST | `/cycles/{id}/activate` | Activar ciclo |
| POST | `/cycles/{id}/close` | Cerrar ciclo |
| PUT | `/cycles/{id}/budgets` | Asignar budget a Area |
| DELETE | `/cycles/{id}/budgets/{area_id}` | Eliminar budget |
| PATCH | `/cycles/{id}/buffer` | Configurar buffer % |
| DELETE | `/cycles/{id}` | Eliminar ciclo |

### Days (`/v1/spaces/{space_id}/days`)
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/days` | Crear dia (idempotente) |
| GET | `/days/{id}` | Detalle de dia |
| GET | `/days/by-date/{date}` | Dia por fecha |
| GET | `/days/by-range?start&end` | Dias en rango (max 365) |
| POST | `/days/{id}/blocks` | Anadir bloque |
| PATCH | `/days/{id}/blocks/{block_id}` | Editar bloque |
| DELETE | `/days/{id}/blocks/{block_id}` | Eliminar bloque |
| DELETE | `/days/{id}/blocks` | Limpiar todos los bloques |

### Day Templates (`/v1/spaces/{space_id}/day-templates`)
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/day-templates` | Crear plantilla |
| GET | `/day-templates` | Listar por Space |
| GET | `/day-templates/{id}` | Detalle |
| PUT | `/day-templates/{id}` | Actualizar nombre y bloques |
| DELETE | `/day-templates/{id}` | Eliminar |
| POST | `/day-templates/{id}/apply` | Aplicar a un dia concreto |

### Week Templates (`/v1/spaces/{space_id}/week-templates`)
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/week-templates` | Crear plantilla semanal |
| GET | `/week-templates` | Listar por Space |
| GET | `/week-templates/{id}` | Detalle |
| DELETE | `/week-templates/{id}` | Eliminar |
| PUT | `/week-templates/{id}/slots/{weekday}` | Asignar DayTemplate a slot |
| DELETE | `/week-templates/{id}/slots/{weekday}` | Limpiar slot |

### Weeks (`/v1/spaces/{space_id}/weeks`)
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| POST | `/weeks` | Crear semana (idempotente) |
| GET | `/weeks/{week_start}` | Detalle (week_start = ISO date lunes) |
| PUT | `/weeks/{week_start}/notes` | Actualizar notas |
| POST | `/weeks/{week_start}/apply-template` | Aplicar WeekTemplate |
| DELETE | `/weeks/{week_start}` | Eliminar con cascada |

### Queries
| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/spaces/{id}/capacity` | Capacity planning por Area |
| GET | `/cards/{id}/eta` | ETA de una Card |

---

## Configuracion

| Variable | Default | Descripcion |
|----------|---------|-------------|
| `SIGMA_APP_TZ` | `Europe/Madrid` | Timezone del dominio |
| `SIGMA_CORS_ORIGINS` | `http://localhost:5173` | Origenes CORS (CSV) |

---

## Tests

| Suite | Tests |
|-------|-------|
| sigma-core unit | 464 |
| sigma-core integration | 42 (requiere emulator Firestore) |
| sigma-rest | 115 |
| **Total** | **621** |

Tests de integracion se skipean automaticamente si el Firestore emulator no esta disponible. Arrancar con `docker-compose up firestore`.

---

## Artefactos

- `openapi.json` — Schema OpenAPI 3.1 completo (60 paths) para referencia del frontend.
