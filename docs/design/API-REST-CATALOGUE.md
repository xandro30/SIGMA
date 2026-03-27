# API-REST-CATALOGUE.md

## SIGMA — Catálogo de API REST

**Versión:** 1.0
**Fecha:** 2026-03-21
**Base URL:** `https://api.sigma.app/v1`

---

## Índice

1. [Convenciones](#1-convenciones)
2. [Autenticación](#2-autenticación)
3. [Spaces](#3-spaces)
4. [Cards](#4-cards)
5. [Areas](#5-areas)
6. [Projects](#6-projects)
7. [Epics](#7-epics)
8. [Errores](#8-errores)

---

## 1. Convenciones

### Formato

- Todas las requests y responses en `application/json`
- Fechas en formato ISO 8601: `"2026-03-21"` (date) / `"2026-03-21T10:30:00Z"` (datetime)
- IDs siempre como `string` UUID v4
- Campos opcionales ausentes se omiten en la response (no se devuelve `null`)

### Verbos HTTP

| Verbo | Uso |
|---|---|
| `GET` | Lectura — no muta estado |
| `POST` | Creación de nuevo recurso |
| `PATCH` | Modificación parcial de recurso existente |
| `DELETE` | Eliminación de recurso |

### Códigos de respuesta

| Código | Significado |
|---|---|
| `200 OK` | Operación exitosa (update, query) |
| `201 Created` | Recurso creado. Incluye `Location` header |
| `204 No Content` | Operación exitosa sin body (delete) |
| `400 Bad Request` | Request malformada o invariante de dominio violado |
| `401 Unauthorized` | Token ausente o inválido |
| `404 Not Found` | Recurso no encontrado |
| `422 Unprocessable Entity` | Regla de negocio violada (WIP limit, transición inválida) |

---

## 2. Autenticación

Todas las rutas requieren autenticación mediante Firebase Auth.

```
Authorization: Bearer <Firebase ID Token>
```

El token se obtiene tras login con Google en el cliente (Firebase SDK). El servidor verifica el token con `firebase-admin` y extrae el `uid` del usuario.

---

## 3. Spaces

### `GET /spaces`

Lista todos los Spaces.

**Response `200`:**
```json
{
  "spaces": [
    {
      "id": "uuid",
      "name": "Work",
      "workflow_states": [
        {
          "id": "uuid",
          "name": "TO DO",
          "order": 1,
          "is_start": true,
          "is_end": false,
          "wip_limit_rules": [],
          "allowed_transitions": ["uuid-wip"]
        },
        {
          "id": "uuid-wip",
          "name": "WIP",
          "order": 2,
          "is_start": false,
          "is_end": false,
          "wip_limit_rules": [
            { "max_cards": 3, "filter": null }
          ],
          "allowed_transitions": ["uuid-done"]
        },
        {
          "id": "uuid-done",
          "name": "DONE",
          "order": 3,
          "is_start": false,
          "is_end": true,
          "wip_limit_rules": [],
          "allowed_transitions": []
        }
      ],
      "created_at": "2026-03-21T10:00:00Z",
      "updated_at": "2026-03-21T10:00:00Z"
    }
  ]
}
```

---

### `POST /spaces`

Crea un nuevo Space.

**Request:**
```json
{ "name": "Work" }
```

**Response `201`:**
```json
{ "id": "uuid", "name": "Work", "workflow_states": [], "created_at": "...", "updated_at": "..." }
```
```
Location: /spaces/{id}
```

---

### `GET /spaces/{spaceId}`

Obtiene un Space por ID.

**Response `200`:** mismo schema que el objeto en `GET /spaces`.

---

### `DELETE /spaces/{spaceId}`

Elimina un Space. Falla si hay Cards activas.

**Response `204`** o **`422`** si hay Cards activas.

---

### `POST /spaces/{spaceId}/workflow-states`

Añade un estado al workflow del Space.

**Request:**
```json
{
  "name": "WIP",
  "order": 2,
  "is_start": false,
  "is_end": false,
  "wip_limit_rules": [
    { "max_cards": 3, "filter": null }
  ],
  "allowed_transitions": ["uuid-done"]
}
```

**Response `200`:** Space completo actualizado.

---

### `PATCH /spaces/{spaceId}/workflow-states/{stateId}`

Actualiza un estado del workflow.

**Request:** mismos campos que POST, todos opcionales.

**Response `200`:** Space completo actualizado.

---

### `DELETE /spaces/{spaceId}/workflow-states/{stateId}`

Elimina un estado del workflow. No se puede eliminar Start ni End. Falla si hay Cards activas en ese estado.

**Response `200`:** Space actualizado, o `422` si hay restricciones.

---

### `GET /spaces/{spaceId}/board`

Datos del tablero: Cards agrupadas por columna (datos ligeros, desde índices).

**Response `200`:**
```json
{
  "pre_workflow": {
    "inbox": [
      { "id": "uuid", "title": "...", "priority": "high", "due_date": "2026-03-25", "labels": ["#SecOps"], "epic_id": null }
    ],
    "refinement": [],
    "backlog": []
  },
  "workflow": {
    "uuid-todo": [...],
    "uuid-wip": [...],
    "uuid-done": []
  }
}
```

---

## 4. Cards

### `GET /spaces/{spaceId}/cards`

Lista Cards del Space con filtros opcionales.

**Query params:**

| Param | Tipo | Descripción |
|---|---|---|
| `priority` | `string` | Comma-separated: `high,critical` |
| `label` | `string` | Uno o más: `?label=SecOps&label=España` |
| `topic` | `string` | Uno o más: `?topic=IAM&topic=GCP` |
| `area_id` | `string` | UUID |
| `project_id` | `string` | UUID |
| `epic_id` | `string` | UUID |
| `pre_workflow_stage` | `string` | `inbox` / `refinement` / `backlog` |
| `workflow_state_id` | `string` | UUID |
| `due_before` | `string` | ISO date |
| `due_after` | `string` | ISO date |

**Response `200`:**
```json
{
  "cards": [
    {
      "id": "uuid",
      "space_id": "uuid",
      "title": "Implementar login con Google",
      "description": "Integrar Firebase Auth...",
      "pre_workflow_stage": null,
      "workflow_state_id": "uuid-wip",
      "area_id": "uuid-area",
      "project_id": "uuid-project",
      "epic_id": "uuid-epic",
      "priority": "high",
      "labels": ["#SecOps", "#España"],
      "topics": ["IAM", "GCP"],
      "urls": ["https://firebase.google.com/docs/auth"],
      "checklist": [
        { "text": "Configurar Firebase project", "done": true },
        { "text": "Deploy a staging", "done": false }
      ],
      "related_cards": ["uuid-card-2"],
      "due_date": "2026-03-25",
      "created_at": "2026-03-21T10:00:00Z",
      "updated_at": "2026-03-21T12:00:00Z"
    }
  ]
}
```

---

### `POST /spaces/{spaceId}/cards`

Crea una nueva Card.

**Request:**
```json
{
  "title": "Revisar WIP limits",
  "description": "...",
  "initial_stage": "inbox",
  "priority": "high",
  "area_id": "uuid",
  "project_id": "uuid",
  "epic_id": "uuid",
  "due_date": "2026-03-28",
  "labels": ["#SecOps"],
  "topics": ["Chronicle"]
}
```

`initial_stage` acepta `PreWorkflowStage` (`inbox`, `refinement`, `backlog`) o un `WorkflowStateId` (UUID). Por defecto: `inbox`.

**Response `201`:** Card completa.

---

### `GET /cards/{cardId}`

Obtiene una Card por ID (documento completo).

**Response `200`:** Card completa (mismo schema que en lista).

---

### `PATCH /cards/{cardId}`

Actualiza campos de metadata de una Card.

**Request** (todos los campos opcionales):
```json
{
  "title": "...",
  "description": "...",
  "priority": "critical",
  "due_date": "2026-04-01",
  "area_id": "uuid",
  "project_id": "uuid",
  "epic_id": "uuid"
}
```

**Response `200`:** Card actualizada.

---

### `DELETE /cards/{cardId}`

Elimina una Card definitivamente.

**Response `204`.**

---

### `PATCH /cards/{cardId}/move`

Mueve una Card entre estados del workflow.

**Request:**
```json
{ "target_state_id": "uuid-wip" }
```

**Response `200`:** Card actualizada, o `422` si transición inválida o WIP limit excedido.

```json
{
  "error": "wip_limit_exceeded",
  "detail": {
    "state_name": "WIP",
    "limit": 3,
    "current": 3
  }
}
```

---

### `PATCH /cards/{cardId}/promote`

Promueve una Card del pre-workflow al workflow.

**Request:**
```json
{ "target_state_id": "uuid-todo" }
```

**Response `200`:** Card actualizada, o `422` si WIP limit excedido.

---

### `PATCH /cards/{cardId}/demote`

Devuelve una Card al pre-workflow.

**Request:**
```json
{ "stage": "backlog" }
```

**Response `200`:** Card actualizada.

---

### `POST /cards/{cardId}/archive`

Mueve la Card al End State del workflow.

**Response `200`:** Card actualizada.

---

### `PATCH /cards/{cardId}/labels`

Gestiona labels de una Card.

**Request:**
```json
{ "action": "add", "label": "#SecOps" }
{ "action": "remove", "label": "#SecOps" }
```

**Response `200`:** Card actualizada.

---

### `PATCH /cards/{cardId}/topics`

Gestiona topics de una Card. Mismo schema que labels.

---

### `PATCH /cards/{cardId}/urls`

Gestiona URLs de una Card.

**Request:**
```json
{ "action": "add", "url": "https://firebase.google.com/docs" }
{ "action": "remove", "url": "https://firebase.google.com/docs" }
```

---

### `POST /cards/{cardId}/checklist`

Añade un ítem al checklist.

**Request:**
```json
{ "text": "Review de seguridad" }
```

**Response `200`:** Card actualizada.

---

### `PATCH /cards/{cardId}/checklist/{text}`

Toggle (completar / reabrir) un ítem del checklist.

**Response `200`:** Card actualizada.

---

### `DELETE /cards/{cardId}/checklist/{text}`

Elimina un ítem del checklist.

**Response `200`:** Card actualizada.

---

### `POST /cards/{cardId}/related`

Añade una Card relacionada (bidireccional).

**Request:**
```json
{ "related_card_id": "uuid" }
```

**Response `200`.**

---

### `DELETE /cards/{cardId}/related/{relatedCardId}`

Elimina una relación entre Cards (bidireccional).

**Response `204`.**

---

## 5. Areas

### `GET /areas`

Lista todas las Areas.

**Response `200`:**
```json
{
  "areas": [
    {
      "id": "uuid",
      "name": "WORK",
      "description": "Plataforma de ciberseguridad",
      "objectives": ["PSOE cert", "Chronicle SOAR prod"],
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

---

### `POST /areas`

**Request:**
```json
{ "name": "WORK", "description": "...", "objectives": ["..."] }
```

**Response `201`:** Area creada.

---

### `PATCH /areas/{areaId}`

**Request** (todos opcionales):
```json
{ "name": "...", "description": "...", "objectives": ["..."] }
```

**Response `200`:** Area actualizada.

---

### `DELETE /areas/{areaId}`

Elimina el Area. Projects y Cards vinculadas quedan con sus referencias a null.

**Response `204`.**

---

## 6. Projects

### `GET /areas/{areaId}/projects`

Lista Projects de un Area.

**Response `200`:**
```json
{
  "projects": [
    {
      "id": "uuid",
      "name": "N3 SecOps",
      "description": "...",
      "objectives": ["YARA-L migration"],
      "area_id": "uuid",
      "status": "active",
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

---

### `POST /areas/{areaId}/projects`

**Request:**
```json
{ "name": "N3 SecOps", "description": "...", "objectives": ["..."] }
```

**Response `201`:** Project creado.

---

### `PATCH /projects/{projectId}`

**Request** (todos opcionales):
```json
{ "name": "...", "description": "...", "objectives": ["..."], "status": "completed", "area_id": "uuid" }
```

**Response `200`:** Project actualizado.

---

### `DELETE /projects/{projectId}`

Cards vinculadas quedan con `project_id: null`.

**Response `204`.**

---

## 7. Epics

### `GET /spaces/{spaceId}/epics`

Lista Epics de un Space.

**Response `200`:**
```json
{
  "epics": [
    {
      "id": "uuid",
      "space_id": "uuid",
      "name": "Auth Module",
      "description": "...",
      "created_at": "...",
      "updated_at": "..."
    }
  ]
}
```

---

### `POST /spaces/{spaceId}/epics`

**Request:**
```json
{ "name": "Auth Module", "description": "..." }
```

**Response `201`:** Epic creada.

---

### `PATCH /epics/{epicId}`

**Request** (todos opcionales):
```json
{ "name": "...", "description": "..." }
```

**Response `200`:** Epic actualizada.

---

### `DELETE /epics/{epicId}`

Cards vinculadas quedan con `epic_id: null`.

**Response `204`.**

---

## 8. Errores

Todos los errores siguen el mismo schema:

```json
{
  "error": "error_code",
  "message": "Descripción legible del error",
  "detail": {}
}
```

| `error` | HTTP | Descripción |
|---|---|---|
| `validation_error` | `400` | Campo inválido en la request |
| `not_found` | `404` | Recurso no encontrado |
| `invalid_transition` | `422` | Transición de estado no permitida |
| `wip_limit_exceeded` | `422` | WIP limit del estado destino alcanzado |
| `invalid_workflow` | `422` | Operación viola un invariante del workflow |
| `unauthorized` | `401` | Token ausente o inválido |
| `internal_error` | `500` | Error interno no esperado |
