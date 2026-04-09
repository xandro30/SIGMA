# SIGMA — Registro de decisiones arquitectonicas

**Ultima revision:** 2026-04-09

Registro consolidado de todas las decisiones de arquitectura del proyecto. Cada entrada documenta *que* se decidio y *por que*. El codigo es la fuente de verdad sobre *como* esta implementado.

---

## Infraestructura

### ADR-001: Mono-repo con dominio compartido
**Estado:** Aceptado

Mono-repo con `uv workspaces`. El dominio vive en `sigma-core` e importa como dependencia local en `sigma-rest` y `sigma-mcp`. `sigma-web` es autonomo con su `package.json`.

**Por que:** Un cambio en el dominio se propaga a todos los adaptadores sin publicar paquetes.

### ADR-002: GCP free tier
**Estado:** Aceptado

Stack completo en GCP: Cloud Run (APIs), Firestore (BD), Firebase Hosting (PWA), Secret Manager (secretos). Todo dentro del free tier permanente.

**Por que:** Coste $0/mes para uso personal. Cold start de 2-4s aceptable.

### ADR-003: Firestore
**Estado:** Aceptado

Firestore como base de datos. Modelado documental con desnormalizacion controlada. Detalle completo en `docs/design/FIRESTORE-DESIGN.md`.

**Por que:** Free tier generoso (50K reads/dia), sin servidor, emulador local para desarrollo.

### ADR-004: Secret Manager + pydantic-settings
**Estado:** Aceptado

GCP Secret Manager con inyeccion nativa en Cloud Run. `pydantic-settings` como capa unificada. `.env` gitignoreado para local.

**Por que:** Credenciales nunca en texto plano. Rotacion sin redespliegue.

### ADR-005: FastMCP + FastAPI
**Estado:** Aceptado (implementacion parcial)

`sigma-rest` con FastAPI (REST, v1 completa). `sigma-mcp` con FastMCP (protocolo MCP, v4 pendiente). Ambos consumen `sigma-core` sin acoplarse a protocolos.

**Por que:** Despliegue independiente por adaptador. Dominio agnostico al protocolo de entrada.

---

## Modelo de dominio

### ADR-006: Bounded Context unico (v1)
**Estado:** Implementado

v1 solo tiene `TaskManagement`. `Planning` (timeboxing, estimaciones) diferido a v2.

### ADR-007: Space como Aggregate Root
**Estado:** Implementado

`Space` contiene `WorkflowState` como entidad interna y `Transition` como array plano. Protege invariantes de workflow: estados unicos, transiciones validas. Start/end determinados por UUIDs reservados (`BEGIN_ID`, `FINISH_ID`).

### ADR-008: Card como Aggregate Root independiente
**Estado:** Implementado

`Card` es AR independiente, referencia `space_id` por ID. Invariantes locales en Card, invariantes cruzados (transiciones, WIP) en casos de uso.

### ADR-009: PreWorkflowStage fijo
**Estado:** Implementado

Enum fijo: `INBOX`, `REFINEMENT`, `BACKLOG`. No configurable. Cards nuevas siempre entran en INBOX. Tres columnas fijas en frontend.

### ADR-010: WIP Limit en caso de uso
**Estado:** Implementado

`MoveCard` valida WIP limit consultando `count_by_state()` antes de mutar. Card y Space permanecen puros.

### ADR-011: Area y Project opcionales (PARA)
**Estado:** Implementado

`Area` y `Project` son opcionales en Card. Jerarquia: Area -> Project -> Epic -> Card. Permite captura rapida en Inbox sin clasificacion previa.

### ADR-012: Column como concepto de presentacion
**Estado:** Implementado

`Column` no es entidad persistida. El frontend compone las columnas con `PreWorkflowStage` (fijo) + `WorkflowState` (configurables).

---

## Practicas de ingenieria

### ADR-013: Testing con pytest
**Estado:** Aceptado

pytest como unico framework. Semantica Given/When/Then como comentarios inline. Dominio sin mocks; fakes para casos de uso; emulador Firestore para integracion.

### ADR-014: Patrones de adaptador
**Estado:** Aceptado

DTOs y Mappers por adaptador. Repositorios Firestore en `sigma-core/infrastructure/` (decision DRY — un solo repo compartido por todos los adaptadores). DI via `dependencies.py` con `lru_cache` + `FastAPI Depends`. Dominio sin dependencias de framework.
