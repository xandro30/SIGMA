# SIGMA — Contrato API REST

**Version:** 1.0.0
**Base URL:** `/v1`
**Ultima revision:** 2026-04-09

> **Nota:** FastAPI genera automaticamente el spec OpenAPI en `/docs` (Swagger UI) y `/openapi.json`. Este documento es la referencia offline.

---

## Convenciones

- Todos los IDs son UUID v4 (string)
- Timestamps en formato ISO 8601
- Fechas (`due_date`) en formato `yyyy-MM-dd`
- Respuestas de listado envueltas en `{ "<recurso>s": [...] }`
- Creacion devuelve `201`, eliminacion devuelve `204`
- Errores de dominio capturados por `SigmaDomainError` handler
- CORS habilitado para `http://localhost:5173`

---

## Health

| Metodo | Path | Respuesta |
|---|---|---|
| `GET` | `/health` | `{"status": "ok"}` |

---

## Spaces

### Modelo: `SpaceResponse`

```json
{
  "id": "string",
  "name": "string",
  "workflow_states": [{"id": "string", "name": "string", "order": 0}],
  "transitions": [{"from_id": "string", "to_id": "string"}],
  "created_at": "string",
  "updated_at": "string"
}
```

### Endpoints

| Metodo | Path | Body | Respuesta | Status |
|---|---|---|---|---|
| `GET` | `/v1/spaces` | — | `{"spaces": [SpaceResponse]}` | 200 |
| `POST` | `/v1/spaces` | `{"name": "string"}` | `SpaceResponse` | 201 |
| `GET` | `/v1/spaces/{space_id}` | — | `SpaceResponse` | 200 |
| `DELETE` | `/v1/spaces/{space_id}` | — | — | 204 |
| `POST` | `/v1/spaces/{space_id}/workflow-states` | `{"name": "string", "order": 0}` | `SpaceResponse` | 201 |
| `DELETE` | `/v1/spaces/{space_id}/workflow-states/{state_id}` | — | `SpaceResponse` | 200 |
| `POST` | `/v1/spaces/{space_id}/transitions` | `{"from_id": "string", "to_id": "string"}` | `SpaceResponse` | 201 |

---

## Areas

### Modelo: `AreaResponse`

```json
{
  "id": "string",
  "name": "string",
  "description": "string | null",
  "objectives": "string | null",
  "color_id": "string | null",
  "created_at": "string",
  "updated_at": "string"
}
```

### Endpoints

| Metodo | Path | Body | Respuesta | Status |
|---|---|---|---|---|
| `GET` | `/v1/areas` | — | `{"areas": [AreaResponse]}` | 200 |
| `POST` | `/v1/areas` | `CreateAreaRequest` | `AreaResponse` | 201 |
| `PATCH` | `/v1/areas/{area_id}` | `UpdateAreaRequest` | `AreaResponse` | 200 |
| `DELETE` | `/v1/areas/{area_id}` | — | — | 204 |
| `GET` | `/v1/areas/{area_id}/epics` | — | `{"epics": [EpicResponse]}` | 200 |

**CreateAreaRequest:**
```json
{"name": "string", "description?": "string", "objectives?": "string", "color_id?": "string"}
```

**UpdateAreaRequest:**
```json
{"name?": "string", "description?": "string", "objectives?": "string", "color_id?": "string"}
```

---

## Projects

### Modelo: `ProjectResponse`

```json
{
  "id": "string",
  "name": "string",
  "description": "string | null",
  "objectives": "string | null",
  "area_id": "string",
  "status": "active | on_hold | completed",
  "created_at": "string",
  "updated_at": "string"
}
```

### Endpoints

| Metodo | Path | Body | Respuesta | Status |
|---|---|---|---|---|
| `GET` | `/v1/areas/{area_id}/projects` | — | `{"projects": [ProjectResponse]}` | 200 |
| `POST` | `/v1/areas/{area_id}/projects` | `CreateProjectRequest` | `ProjectResponse` | 201 |
| `GET` | `/v1/projects/{project_id}` | — | `ProjectResponse` | 200 |
| `PATCH` | `/v1/projects/{project_id}` | `UpdateProjectRequest` | `ProjectResponse` | 200 |
| `DELETE` | `/v1/projects/{project_id}` | — | — | 204 |

**CreateProjectRequest:**
```json
{"name": "string", "description?": "string", "objectives?": "string"}
```

**UpdateProjectRequest:**
```json
{"name?": "string", "description?": "string", "objectives?": "string", "status?": "string"}
```

---

## Epics

### Modelo: `EpicResponse`

```json
{
  "id": "string",
  "space_id": "string",
  "project_id": "string",
  "area_id": "string",
  "name": "string",
  "description": "string | null",
  "created_at": "string",
  "updated_at": "string"
}
```

### Endpoints

| Metodo | Path | Body | Respuesta | Status |
|---|---|---|---|---|
| `GET` | `/v1/spaces/{space_id}/epics` | — | `{"epics": [EpicResponse]}` | 200 |
| `POST` | `/v1/spaces/{space_id}/epics` | `CreateEpicRequest` | `EpicResponse` | 201 |
| `GET` | `/v1/epics/{epic_id}` | — | `EpicResponse` | 200 |
| `PATCH` | `/v1/epics/{epic_id}` | `UpdateEpicRequest` | `EpicResponse` | 200 |
| `DELETE` | `/v1/epics/{epic_id}` | — | — | 204 |

**CreateEpicRequest:**
```json
{"name": "string", "project_id": "string", "description?": "string"}
```

**UpdateEpicRequest:**
```json
{"name?": "string", "description?": "string"}
```

---

## Cards

### Modelo: `CardResponse`

```json
{
  "id": "string",
  "space_id": "string",
  "title": "string",
  "description": "string | null",
  "pre_workflow_stage": "inbox | refinement | backlog | null",
  "workflow_state_id": "string | null",
  "area_id": "string | null",
  "project_id": "string | null",
  "epic_id": "string | null",
  "priority": "low | medium | high | critical | null",
  "labels": ["string"],
  "topics": ["string"],
  "urls": ["string"],
  "checklist": [{"text": "string", "done": true}],
  "related_cards": ["string"],
  "due_date": "yyyy-MM-dd | null",
  "created_at": "string",
  "updated_at": "string"
}
```

### CRUD

| Metodo | Path | Body | Respuesta | Status |
|---|---|---|---|---|
| `GET` | `/v1/spaces/{space_id}/cards` | — | `{"cards": [CardResponse]}` | 200 |
| `POST` | `/v1/spaces/{space_id}/cards` | `CreateCardRequest` | `CardResponse` | 201 |
| `GET` | `/v1/cards/{card_id}` | — | `CardResponse` | 200 |
| `PATCH` | `/v1/cards/{card_id}` | `UpdateCardRequest` | `CardResponse` | 200 |
| `DELETE` | `/v1/cards/{card_id}` | — | — | 204 |

**CreateCardRequest:**
```json
{
  "title": "string",
  "initial_stage?": "inbox (default)",
  "description?": "string",
  "priority?": "string",
  "area_id?": "string",
  "project_id?": "string",
  "epic_id?": "string",
  "due_date?": "string",
  "labels?": ["string"],
  "topics?": ["string"]
}
```

**UpdateCardRequest** (usa `model_fields_set` para distinguir entre no enviado y `null`):
```json
{
  "title?": "string",
  "description?": "string",
  "priority?": "string",
  "due_date?": "string",
  "area_id?": "string",
  "epic_id?": "string",
  "labels?": ["string"]
}
```

### Movimiento de Cards

| Metodo | Path | Body | Descripcion |
|---|---|---|---|
| `PATCH` | `/v1/cards/{card_id}/move` | `{"target_state_id": "string"}` | Mover dentro del workflow |
| `PATCH` | `/v1/cards/{card_id}/promote` | `{"target_state_id?": "string"}` | Triage -> Workflow |
| `PATCH` | `/v1/cards/{card_id}/demote` | `{"stage?": "backlog"}` | Workflow -> Triage (solo refinement/backlog) |
| `PATCH` | `/v1/cards/{card_id}/triage-stage` | `{"stage": "string"}` | Mover dentro del triage |
| `POST` | `/v1/cards/{card_id}/archive` | — | Archivar (mover al End State) |

### Clasificacion PARA

| Metodo | Path | Body | Descripcion |
|---|---|---|---|
| `PATCH` | `/v1/cards/{card_id}/area` | `{"area_id": "string | null"}` | Asignar/quitar Area |
| `PATCH` | `/v1/cards/{card_id}/project` | `{"project_id": "string | null"}` | Asignar/quitar Project |
| `PATCH` | `/v1/cards/{card_id}/epic` | `{"epic_id": "string | null"}` | Asignar/quitar Epic |

### Operaciones sobre listas

| Metodo | Path | Body | Descripcion |
|---|---|---|---|
| `PATCH` | `/v1/cards/{card_id}/labels` | `{"action": "add|remove", "label": "string"}` | Gestionar labels |
| `PATCH` | `/v1/cards/{card_id}/topics` | `{"action": "add|remove", "topic": "string"}` | Gestionar topics |
| `PATCH` | `/v1/cards/{card_id}/urls` | `{"action": "add|remove", "url": "string"}` | Gestionar URLs |

### Checklist

| Metodo | Path | Body | Descripcion |
|---|---|---|---|
| `POST` | `/v1/cards/{card_id}/checklist` | `{"text": "string"}` | Anadir item |
| `PATCH` | `/v1/cards/{card_id}/checklist/{text}` | — | Toggle done/undone |
| `DELETE` | `/v1/cards/{card_id}/checklist/{text}` | — | Eliminar item |

### Relaciones

| Metodo | Path | Body | Descripcion |
|---|---|---|---|
| `POST` | `/v1/cards/{card_id}/related` | `{"related_card_id": "string"}` | Relacionar cards (simetrica) |
| `DELETE` | `/v1/cards/{card_id}/related/{related_card_id}` | — | Eliminar relacion |

---

## Resumen

| Recurso | GET | POST | PATCH | DELETE | Total |
|---|---|---|---|---|---|
| Health | 1 | — | — | — | 1 |
| Spaces | 2 | 2 | — | 2 | 6 |
| Areas | 2 | 1 | 1 | 1 | 5 |
| Projects | 2 | 1 | 1 | 1 | 5 |
| Epics | 2 | 1 | 1 | 1 | 5 |
| Cards | 2 | 3 | 10 | 3 | 18 |
| **Total** | **11** | **8** | **13** | **8** | **40** |
