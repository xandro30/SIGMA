# v3 Metrics BC — Release Notes

**Fecha:** 2026-04-12
**Scope:** Backend completo del bounded context `metrics` (sigma-core + sigma-rest).
**Depende de:** Plan 2 — Planning BC (tag v2-planning-bc-backend).

---

## Domain Events Infrastructure (shared_kernel)

Nuevo sistema de domain events in-process reutilizable por cualquier BC:

- `DomainEvent` base + `CycleClosed` evento inter-BC (shared_kernel)
- `EventBus` protocol + `InProcessEventBus` (handlers secuenciales, fallo atomico)
- `EventEmitterMixin` para aggregates que acumulan eventos
- Cycle hereda EventEmitterMixin y emite `CycleClosed` al cerrarse
- CloseCycle despacha eventos via EventBus tras persistir

---

## Card: entered_workflow_at

Nuevo campo `entered_workflow_at: Timestamp | None` en Card (task_management):

- Se setea en `move_to_workflow_state` cuando la card viene de triage (pre_workflow)
- Se limpia en `move_to_pre_workflow`
- Semantica: ultima entrada al workflow (se sobreescribe al re-promover)
- Serializado en mappers Firestore
- Necesario para cycle time (completed_at - entered_workflow_at)

---

## Aggregates

### CycleSummary (inmutable, jerarquico)
Metricas precalculadas en estructura de arbol PARA: global → area → project → epic.

Generado automaticamente al cerrar un ciclo via domain event `CycleClosed`.

Cada nivel contiene un `MetricsBlock`:
- `total_cards_completed`
- `avg_cycle_time_minutes` (completed_at - entered_workflow_at)
- `avg_lead_time_minutes` (completed_at - created_at)
- `consumed_minutes` (sum de size_mapping[card.size])
- `calibration_entries` (estimated vs actual para cards con size y actual_time)

Nivel area incluye `budget_minutes`. Nivel project incluye epics anidados.

### CycleSnapshot (inmutable, raw copy)
Copia raw de los datos del ciclo al momento de cerrarlo:
- Cards completadas como `CardSnapshot` (card_id, area_id, project_id, epic_id, size, actual_time, timestamps)
- Area budgets, buffer_percentage, size_mapping
- Permite recalcular metricas futuras sin depender del estado actual de cards/spaces

---

## MetricsCalculator (servicio puro de dominio)

Sin I/O, sin estado. Building block `_calculate_block` invocado por nivel:
- Global: todas las cards
- Area: cards filtradas por area_id
- Project: cards filtradas por project_id dentro del area
- Epic: cards filtradas por epic_id dentro del project

Cards sin area_id solo aparecen en global. Sin project_id solo en area.metrics. Sin epic_id solo en project.metrics.

---

## Queries

### GetMetrics (dual approach)
- Ciclo cerrado: lee CycleSummary persistido (source="snapshot")
- Ciclo activo: calcula on-demand con MetricsCalculator (source="on_demand")
- Sin cycle_id: busca ciclo activo del Space

### GetSnapshot
- Devuelve CycleSnapshot raw de un ciclo cerrado

---

## REST API — Metrics endpoints

### Metricas (arbol jerarquico)

```
GET /v1/spaces/{space_id}/metrics?cycle_id={id}
```

Response: arbol completo con global_metrics + areas (cada una con projects, cada uno con epics). Campo `source` indica "snapshot" u "on_demand".

### Snapshot raw

```
GET /v1/spaces/{space_id}/metrics/snapshots/{cycle_id}
```

Solo ciclos cerrados. Devuelve CycleSnapshot con todas las CardSnapshots.

---

## Colecciones Firestore

- `cycle_summaries` — metricas precalculadas jerarquicas
- `cycle_snapshots` — raw copy de datos del ciclo

---

## Tests

| Suite | Tests |
|-------|-------|
| sigma-core unit | 494 |
| sigma-core integration | 42 (requiere emulator) |
| sigma-rest | 120 |
| **Total** | **656** |

Nuevos tests respecto a v2: +30 unit (entered_workflow_at, EventBus, MetricsCalculator, cycle events) + 5 REST integration (metrics endpoints).

---

## Artefactos

- `openapi.json` — Schema OpenAPI 3.1 completo (62 paths)
