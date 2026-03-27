# MCP-TOOLS-CATALOGUE.md

## SIGMA — Catálogo de MCP Tools

**Versión:** 1.0
**Fecha:** 2026-03-21
**Protocolo:** Model Context Protocol (MCP) — Streamable HTTP

---

## Índice

1. [Principios de diseño](#1-principios-de-diseño)
2. [Tools de Spaces](#2-tools-de-spaces)
3. [Tools de Cards — Ciclo de vida](#3-tools-de-cards--ciclo-de-vida)
4. [Tools de Cards — Contenido](#4-tools-de-cards--contenido)
5. [Tools de Cards — Consultas](#5-tools-de-cards--consultas)
6. [Tools de Areas y Projects](#6-tools-de-areas-y-projects)
7. [Tools de Epics](#7-tools-de-epics)

---

## 1. Principios de diseño

### Orientadas a intención, no a CRUD

Las MCP tools están diseñadas para que Claude las invoque de forma natural según la intención del usuario, no como una API CRUD directa. Los nombres son verbos de acción en inglés siguiendo las convenciones MCP.

### Parámetros explícitos y descritos

Cada parámetro tiene descripción que guía al modelo en su uso correcto. Los parámetros opcionales tienen valores por defecto claros.

### Respuestas orientadas a confirmación

Las tools devuelven resúmenes legibles + datos estructurados. Claude usa los datos estructurados para encadenar operaciones y el resumen para responder al usuario.

### Errores como datos

Los errores de negocio (WIP limit, transición inválida) se devuelven como respuestas estructuradas, no como excepciones — Claude puede razonar sobre ellos y proponer alternativas.

---

## 2. Tools de Spaces

---

### `list_spaces`

Lista todos los Spaces disponibles.

**Parámetros:** ninguno.

**Retorna:**
```json
{
  "spaces": [
    {
      "id": "uuid",
      "name": "Work",
      "workflow_states_count": 3,
      "workflow_states": [
        { "id": "uuid", "name": "TO DO", "is_start": true, "is_end": false },
        { "id": "uuid", "name": "WIP",   "is_start": false, "is_end": false, "wip_limit": 3 },
        { "id": "uuid", "name": "DONE",  "is_start": false, "is_end": true }
      ]
    }
  ],
  "summary": "2 spaces: Work, Personal"
}
```

---

### `get_space`

Obtiene los detalles de un Space, incluyendo su workflow completo.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `space_id` | `string` | ✓ | UUID del Space |

**Retorna:** Space completo con todos sus WorkflowStates y reglas WIP.

---

### `create_space`

Crea un nuevo Space.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `name` | `string` | ✓ | Nombre del Space (máx. 100 chars) |

**Retorna:**
```json
{
  "id": "uuid",
  "name": "Personal",
  "message": "Space 'Personal' created. No workflow states yet — use add_workflow_state to configure it."
}
```

---

### `add_workflow_state`

Añade un estado al workflow de un Space.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `space_id` | `string` | ✓ | UUID del Space |
| `name` | `string` | ✓ | Nombre del estado |
| `order` | `integer` | ✓ | Posición en el tablero (1 = izquierda) |
| `is_start` | `boolean` | ✗ | Estado de entrada al workflow. Default: `false` |
| `is_end` | `boolean` | ✗ | Estado terminal. Default: `false` |
| `wip_limit` | `integer` | ✗ | Límite de Cards simultáneas (aplica a todas). Omitir = sin límite |
| `allowed_transitions` | `array[string]` | ✗ | IDs de estados destino permitidos. Omitir o `[]` = todas permitidas |

**Retorna:**
```json
{
  "state_id": "uuid",
  "message": "State 'WIP' added to workflow with WIP limit of 3."
}
```

---

## 3. Tools de Cards — Ciclo de vida

---

### `create_card`

Crea una nueva Card.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `space_id` | `string` | ✓ | UUID del Space donde se crea la Card |
| `title` | `string` | ✓ | Título de la Card (1–255 chars) |
| `initial_stage` | `string` | ✗ | Etapa inicial. Valores: `inbox` (default), `refinement`, `backlog`, o UUID de WorkflowState para entrada urgente |
| `description` | `string` | ✗ | Descripción detallada |
| `priority` | `string` | ✗ | `low`, `medium`, `high`, `critical` |
| `area_id` | `string` | ✗ | UUID del Area |
| `project_id` | `string` | ✗ | UUID del Project |
| `epic_id` | `string` | ✗ | UUID del Epic |
| `due_date` | `string` | ✗ | Fecha límite ISO: `"2026-03-28"` |
| `labels` | `array[string]` | ✗ | Labels libres: `["#SecOps", "#España"]` |
| `topics` | `array[string]` | ✗ | Topics técnicos: `["IAM", "GCP"]` |

**Retorna:**
```json
{
  "id": "uuid",
  "title": "Revisar WIP limits",
  "stage": "inbox",
  "message": "Card 'Revisar WIP limits' created in INBOX."
}
```

---

### `move_card`

Mueve una Card entre estados del workflow (valida transición y WIP limits).

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `card_id` | `string` | ✓ | UUID de la Card |
| `target_state_id` | `string` | ✓ | UUID del WorkflowState destino |

**Retorna (éxito):**
```json
{
  "card_id": "uuid",
  "from_state": "TO DO",
  "to_state": "WIP",
  "message": "Card moved from 'TO DO' to 'WIP'."
}
```

**Retorna (WIP limit):**
```json
{
  "success": false,
  "error": "wip_limit_exceeded",
  "state": "WIP",
  "limit": 3,
  "current": 3,
  "message": "Cannot move card to 'WIP': limit of 3 reached. Complete a task first."
}
```

**Retorna (transición inválida):**
```json
{
  "success": false,
  "error": "invalid_transition",
  "from_state": "TO DO",
  "to_state": "DONE",
  "message": "Transition from 'TO DO' to 'DONE' is not allowed in this workflow."
}
```

---

### `promote_card_to_workflow`

Promueve una Card desde el pre-workflow (Inbox/Refinement/Backlog) al workflow.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `card_id` | `string` | ✓ | UUID de la Card |
| `target_state_id` | `string` | ✗ | UUID del WorkflowState destino. Si se omite, se usa el Start State del Space |

**Retorna:**
```json
{
  "card_id": "uuid",
  "from_stage": "backlog",
  "to_state": "TO DO",
  "message": "Card promoted to workflow state 'TO DO'."
}
```

---

### `demote_card_to_pre_workflow`

Devuelve una Card del workflow al pre-workflow.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `card_id` | `string` | ✓ | UUID de la Card |
| `stage` | `string` | ✗ | `inbox`, `refinement`, `backlog`. Default: `backlog` |

**Retorna:**
```json
{
  "card_id": "uuid",
  "from_state": "WIP",
  "to_stage": "backlog",
  "message": "Card demoted back to BACKLOG."
}
```

---

### `archive_card`

Mueve una Card al estado End del workflow.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `card_id` | `string` | ✓ | UUID de la Card |

**Retorna:**
```json
{
  "card_id": "uuid",
  "message": "Card archived (moved to DONE)."
}
```

---

### `delete_card`

Elimina una Card definitivamente.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `card_id` | `string` | ✓ | UUID de la Card |
| `confirm` | `boolean` | ✓ | Debe ser `true` para confirmar la eliminación irreversible |

**Retorna:**
```json
{ "message": "Card deleted permanently." }
```

---

## 4. Tools de Cards — Contenido

---

### `update_card`

Actualiza campos de metadata de una Card.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `card_id` | `string` | ✓ | UUID de la Card |
| `title` | `string` | ✗ | Nuevo título |
| `description` | `string` | ✗ | Nueva descripción |
| `priority` | `string` | ✗ | `low`, `medium`, `high`, `critical`, o `null` para eliminar |
| `due_date` | `string` | ✗ | ISO date, o `null` para eliminar |
| `area_id` | `string` | ✗ | UUID del Area, o `null` para desvincular |
| `project_id` | `string` | ✗ | UUID del Project, o `null` para desvincular |
| `epic_id` | `string` | ✗ | UUID del Epic, o `null` para desvincular |

**Retorna:**
```json
{ "card_id": "uuid", "updated_fields": ["priority", "due_date"], "message": "Card updated." }
```

---

### `add_label`

Añade una label a una Card.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `card_id` | `string` | ✓ | |
| `label` | `string` | ✓ | Label libre, ej: `"#SecOps"` |

---

### `remove_label`

Elimina una label de una Card.

**Parámetros:** `card_id`, `label`.

---

### `add_topic`

Añade un topic técnico a una Card.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `card_id` | `string` | ✓ | |
| `topic` | `string` | ✓ | Topic técnico, ej: `"IAM"`, `"Chronicle"` |

---

### `remove_topic`

Elimina un topic de una Card.

**Parámetros:** `card_id`, `topic`.

---

### `add_url`

Añade una URL de referencia a una Card.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `card_id` | `string` | ✓ | |
| `url` | `string` | ✓ | URL válida (http/https) |

---

### `remove_url`

Elimina una URL de una Card.

**Parámetros:** `card_id`, `url`.

---

### `add_checklist_item`

Añade un ítem al checklist de una Card.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `card_id` | `string` | ✓ | |
| `text` | `string` | ✓ | Texto del ítem (1–500 chars) |

---

### `toggle_checklist_item`

Marca como completado o reabre un ítem del checklist.

**Parámetros:** `card_id`, `text` (texto exacto del ítem).

**Retorna:**
```json
{ "text": "Deploy a staging", "done": true, "progress": "7/8 items completed" }
```

---

### `remove_checklist_item`

Elimina un ítem del checklist.

**Parámetros:** `card_id`, `text`.

---

### `add_related_card`

Relaciona dos Cards (relación bidireccional y simétrica).

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `card_id` | `string` | ✓ | UUID de la primera Card |
| `related_card_id` | `string` | ✓ | UUID de la Card a relacionar |

**Retorna:**
```json
{ "message": "Cards linked bidirectionally." }
```

---

### `remove_related_card`

Elimina la relación entre dos Cards.

**Parámetros:** `card_id`, `related_card_id`.

---

## 5. Tools de Cards — Consultas

---

### `get_card`

Obtiene el detalle completo de una Card.

**Parámetros:** `card_id`.

**Retorna:** Card completa con todos sus campos.

---

### `list_cards`

Lista Cards con filtros opcionales.

**Parámetros:**

| Param | Tipo | Req | Descripción |
|---|---|---|---|
| `space_id` | `string` | ✓ | UUID del Space |
| `priority` | `array[string]` | ✗ | Filtrar por prioridades: `["high", "critical"]` |
| `labels` | `array[string]` | ✗ | Cards que tengan alguno de estos labels |
| `topics` | `array[string]` | ✗ | Cards que tengan alguno de estos topics |
| `area_id` | `string` | ✗ | Filtrar por Area |
| `project_id` | `string` | ✗ | Filtrar por Project |
| `epic_id` | `string` | ✗ | Filtrar por Epic |
| `stage` | `string` | ✗ | `inbox`, `refinement`, `backlog`, o UUID de WorkflowState |
| `due_before` | `string` | ✗ | ISO date |
| `due_after` | `string` | ✗ | ISO date |

**Retorna:**
```json
{
  "cards": [...],
  "total": 14,
  "summary": "14 cards in Work: 3 in WIP, 2 overdue, 1 critical"
}
```

---

### `get_board`

Obtiene la vista del tablero completo de un Space, agrupado por columnas.

**Parámetros:** `space_id`.

**Retorna:**
```json
{
  "space": { "id": "uuid", "name": "Work" },
  "pre_workflow": {
    "inbox": { "count": 3, "cards": [...] },
    "refinement": { "count": 1, "cards": [...] },
    "backlog": { "count": 5, "cards": [...] }
  },
  "workflow": {
    "TO DO": { "state_id": "uuid", "count": 2, "wip_limit": null, "cards": [...] },
    "WIP":   { "state_id": "uuid", "count": 2, "wip_limit": 3, "cards": [...] },
    "DONE":  { "state_id": "uuid", "count": 0, "cards": [] }
  },
  "summary": "Board 'Work': 11 active cards. WIP at 2/3."
}
```

---

## 6. Tools de Areas y Projects

---

### `list_areas`

Lista todas las Areas con sus Projects.

**Parámetros:** ninguno.

**Retorna:**
```json
{
  "areas": [
    {
      "id": "uuid", "name": "WORK", "description": "...",
      "projects": [
        { "id": "uuid", "name": "N3 SecOps", "status": "active", "cards_count": 14 }
      ]
    }
  ]
}
```

---

### `create_area`

**Parámetros:** `name`, `description?`, `objectives?`.

---

### `update_area`

**Parámetros:** `area_id`, `name?`, `description?`, `objectives?`.

---

### `create_project`

**Parámetros:** `name`, `area_id`, `description?`, `objectives?`.

---

### `update_project`

**Parámetros:** `project_id`, `name?`, `description?`, `objectives?`, `status?`, `area_id?`.

---

## 7. Tools de Epics

---

### `list_epics`

Lista los Epics de un Space con sus Cards.

**Parámetros:** `space_id`.

**Retorna:**
```json
{
  "epics": [
    {
      "id": "uuid", "name": "Auth Module",
      "cards_total": 10, "cards_completed": 6,
      "progress": "60%"
    }
  ]
}
```

---

### `create_epic`

**Parámetros:** `space_id`, `name`, `description?`.

---

### `update_epic`

**Parámetros:** `epic_id`, `name?`, `description?`.
