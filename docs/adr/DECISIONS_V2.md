# SIGMA v2 — Registro de decisiones arquitectonicas

**Ultima revision:** 2026-04-10

Registro de decisiones de arquitectura para SIGMA v2. Cada version de SIGMA mantiene su propio registro empezando desde ADR-001. Las decisiones de v1 viven en `DECISIONS.md`.

---

## Modelo de dominio

### ADR-001: Bounded contexts `planning` y `metrics`
**Estado:** Aceptado — 2026-04-10
**Supersede parcialmente:** v1 ADR-006 (aplazamiento de Planning a v2)

v2 introduce dos nuevos bounded contexts junto a `task_management`:

- **`planning`** — planificacion temporal. Aggregates: `Cycle`, `DayTemplate`, `Day`, `WeekTemplate`, `Week`. No conoce Cards; usa `space_id` y `area_id` como FKs blandas.
- **`metrics`** — calculo y persistencia de metricas. Aggregate: `CycleSummary` (solo ciclos cerrados, inmutable). Metricas de ciclos activos se calculan on-demand reutilizando el mismo `MetricsCalculator` puro.

`task_management` se extiende (no se divide) con: `size`, timer, Eisenhower (`urgency` + `importance`), `energy`, `blocked_by`, `class_of_service`, WIP limits operativos (soft warning, no block).

Relaciones entre BCs via IDs por valor — sin imports cruzados entre aggregates. Coordinacion en use cases (ej: `CloseCycle` en `planning` dispara `CreateCycleSummary` en `metrics`).

**Por que:** separa responsabilidades temporales y analiticas del nucleo de tareas. `task_management` no se hincha con conceptos de ciclos, time blocks ni metricas. Tests y evolucion independientes por BC. Alternativa descartada: 4 BCs separando estimation (estimation es propiedad natural de Card).

---

### ADR-002: Cycle como propiedad global del Space
**Estado:** Aceptado — 2026-04-10

Un `Space` tiene un unico ciclo activo (`active_cycle_id: CycleId | None`). No hay ciclos por Area. La asociacion Card ↔ Cycle es **implicita por rango de fechas** — una card cuenta en un ciclo si su `completed_at` cae dentro de `[cycle.start_date, cycle.end_date]`. No hay FK `Card.cycle_id`.

**Por que:** el ciclo es el "intervalo minimo de reciclado del trabajo activo no completado" del Space completo — un sprint unificado, no fragmentado por Area. La asociacion por fechas evita inconsistencias si se reajusta un ciclo y simplifica queries de metricas.

---

### ADR-003: Reset de datos al desplegar v2
**Estado:** Aceptado — 2026-04-10

v2 parte de Firestore vacio. No hay migracion desde v1. Los mappers escriben y leen el esquema v2 sin fallbacks ni `.get("campo", default)`. Cero codigo de compatibilidad hacia atras.

**Por que:** SIGMA es uso personal, no productivo. Sin datos criticos que preservar. Un reset limpio evita polucion de codigo con branches v1/v2 y permite un modelo v2 consistente desde el primer commit.

---

### ADR-004: Nuevo Bounded Context `tracking` para sesiones de trabajo y registro de tiempo
**Estado:** Aceptado — 2026-04-13
**Rama:** `feat/tracking-bc-work-sessions`

#### Contexto

El BC `task_management` gestiona el estado de las cards y acumula `actual_time` via timer (`start_timer` / `stop_timer`). Sin embargo, el concepto de "sesion de trabajo activa" — con tecnica de concentracion (Pomodoro), vitacora de trabajo y sincronizacion multi-dispositivo — es ajeno a la gestion de tareas. Necesita un hogar propio.

Adicionalmente, el BC `metrics` calcula `consumed_minutes` como estimacion (size_mapping), pero no dispone de `actual_consumed_minutes` (suma real de tiempo trabajado). Esta brecha impide comparar estimacion vs realidad a nivel de ciclo.

#### Decision

Introducir el BC `tracking` con los siguientes elementos:

**Nuevos artefactos:**

- `WorkSession` (aggregate + `EventEmitterMixin`): sesion activa de trabajo. Una por space (enforzado por `document_id = space_id` en Firestore). Contiene `Timer` (tecnica + config) para restaurar estado en refresh. Emite `WorkSessionCompleted` al completarse o detenerse con guardado.
- `TrackingEntry` (aggregate inmutable): registro permanente de un bloque de tiempo. Campos: `entry_type` (Work | Event | Travel | ...), `description`, `minutes` (tiempo total del bloque incluyendo descansos), referencias opcionales a `area_id`, `project_id`, `epic_id`, `card_id`.
- `Timer` (value object): encapsula la tecnica de concentracion y su configuracion. Hoy: `TimerTechnique.POMODORO` con `work_minutes`, `break_minutes`, `num_rounds`. Extensible sin modificar `WorkSession`.
- `WorkSessionCompleted` (DomainEvent inter-BC): definido en `shared_kernel/events.py`, igual que `CycleClosed`. Contrato tracking → task_management.

**Cambios en BCs existentes:**

- `task_management / Card`: añade `work_log: list[WorkLogEntry]` y metodo `add_work_log(entry)` que acumula en `actual_time`. `WorkLogEntry` (value object): `log`, `minutes`, `logged_at`.
- `metrics / MetricsBlock`: añade `actual_consumed_minutes: int` (suma de `actual_time_minutes` de cards completadas). `MetricsCalculator` lo computa junto a `consumed_minutes` estimado.

**Flujo de evento (mismo patron que `CycleClosed`):**

```
WorkSession.complete()
  → _record_event(WorkSessionCompleted)

StopWorkSession (use case)
  → session_repo.save()
  → collect_events() → event_bus.publish()

OnWorkSessionCompletedHandler (task_management BC)
  → card.add_work_log(WorkLogEntry)
  → card_repo.save(card)

main.py
  → bus.subscribe(WorkSessionCompleted, OnWorkSessionCompletedHandler)
```

**Tiempo registrado:** `session_ended_at − session_started_at` (bloque completo, descansos incluidos). Esto alinea con los budgets de ciclo, que miden dedicacion total, no foco puro.

#### Opciones descartadas

| Opcion | Razon del descarte |
|--------|--------------------|
| `WorkSession` en `task_management` | No es gestion de tareas; contamina el BC con conceptos de tiempo y tecnicas de concentracion |
| `CardWorkLogPort` (llamada directa cross-BC) | Acopla `tracking` a `task_management`; rompe el aislamiento entre BCs |
| Event bus externo (Pub/Sub, Redis Streams) | Overkill para herramienta personal de uso local/single-user |

#### Trade-offs

| Dimension | Evaluacion |
|-----------|------------|
| Aislamiento BC | Alto — tracking no importa nada de task_management |
| Consistencia eventual | El handler puede fallar tras persistir la sesion. Mitigacion: idempotencia en `add_work_log` (misma entrada no se duplica si logged_at coincide) |
| Extensibilidad | Alta — `EntryType` y `TimerTechnique` son extensibles sin cambios en aggregates |
| Complejidad operativa | Baja — mismo event bus in-process ya en uso |

#### Riesgos y mitigaciones

| Riesgo | Mitigacion |
|--------|------------|
| `WorkSession` zombie (cliente cae sin cerrar) | Campo `expires_at`; frontend detecta sesion expirada en `GET /work-session` al recargar |
| Race condition en creacion de sesion (multi-dispositivo) | Aceptado conscientemente — SIGMA es personal (un usuario por space). Probabilidad practica: nula. Documentado en `StartWorkSession.execute` con comentario explicito. |
| `actual_consumed_minutes` = 0 en cards sin timer usado | Campo opcional en UI; metricas muestran estimado cuando real = 0 |

#### Consecuencias

- Los budgets de ciclo ganan una contrapartida real: `actual_consumed_minutes` vs `consumed_minutes` vs `budget_minutes`.
- La vitacora de trabajo (`work_log` en Card) provee historial de sesiones por tarea.
- El patron `EventEmitterMixin` + `InProcessEventBus` queda consolidado como mecanismo estandar de coordinacion inter-BC en SIGMA.
- `TrackingEntry` sienta la base para registrar otros tipos de actividad (eventos, viajes, aprendizaje) sin modificar BCs existentes.
