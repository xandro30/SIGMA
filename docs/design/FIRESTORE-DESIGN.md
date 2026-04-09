# FIRESTORE-DESIGN.md

## SIGMA — Diseño de base de datos Firestore

**Versión:** 1.1
**Fecha:** 2026-03-21
**Última revisión:** 2026-04-09
**Complementa:** ADR-003 (activo — Firestore sigue siendo la base de datos)

---

## Índice

1. [Principios de modelado](#1-principios-de-modelado)
2. [Colecciones y estructura de documentos](#2-colecciones-y-estructura-de-documentos)
3. [Estrategia de escritura](#3-estrategia-de-escritura)
4. [Índices compuestos](#4-índices-compuestos)
5. [Patrones de consulta](#5-patrones-de-consulta)
6. [Seguridad](#6-seguridad)
7. [Límites y consideraciones](#7-límites-y-consideraciones)

---

## 1. Principios de modelado

Firestore es una base de datos documental NoSQL. El modelo no se diseña desde las entidades sino desde los **patrones de lectura** — las consultas definen la estructura.

**Decisiones base:**

- **Un documento por Aggregate Root** — `cards`, `spaces`, `areas`, `projects`, `epics`
- **Desnormalización controlada** — datos duplicados donde acelera lecturas frecuentes, con fanout en escritura para mantener consistencia
- **Sin joins** — toda la información necesaria para una vista se obtiene en una o dos consultas
- **Transacciones atómicas** para operaciones que afectan múltiples documentos

---

## 2. Colecciones y estructura de documentos

### 2.1 `/spaces/{spaceId}`

Contiene el workflow completo embebido — `WorkflowState` y `Transition` no tienen colecciones propias.

```
spaces/{spaceId}
  id:               string          # UUID v4
  name:             string
  workflow_states:  array<object>   # embebido — entidad interna de Space
    - id:           string          # WorkflowStateId (UUID v4)
      name:         string
      order:        number
  transitions:      array<object>   # grafo de transiciones permitidas
    - from_id:      string          # WorkflowStateId origen
      to_id:        string          # WorkflowStateId destino
  created_at:       timestamp
  updated_at:       timestamp
```

**Notas de implementación:**

- `workflow_states` almacena solo `{id, name, order}`. Las reglas WIP limit y los filtros se evalúan en dominio, no se persisten por estado.
- El estado inicial y el estado final se identifican mediante UUIDs reservados definidos en `sigma_core` (`BEGIN_ID`, `FINISH_ID`), no mediante flags `is_start` / `is_end`.
- Las transiciones permitidas se almacenan como array plano en el documento Space, no embebidas en cada estado.
- Las transiciones vacías (`[]`) significan que ninguna transición está definida — el dominio controla cómo interpreta eso.

**Justificación del embedding:** `WorkflowState` es una entidad interna de `Space` sin identidad propia. Nunca se consulta de forma independiente. Embedding elimina lecturas adicionales en cada validación de transición.

---

### 2.2 `/cards/{cardId}`

Documento principal de Card. Fuente de verdad.

```
cards/{cardId}
  id:                     string        # UUID v4
  space_id:               string        # referencia a /spaces/{spaceId}
  title:                  string
  description:            string | null
  pre_workflow_stage:     string | null  # "inbox" | "refinement" | "backlog"
  workflow_state_id:      string | null  # WorkflowStateId
  area_id:                string | null  # referencia a /areas/{areaId}
  project_id:             string | null  # referencia a /projects/{projectId}
  epic_id:                string | null  # referencia a /epics/{epicId}
  priority:               string | null  # "low" | "medium" | "high" | "critical"
  labels:                 array<string>
  topics:                 array<string>
  urls:                   array<string>
  checklist:              array<object>
    - text:               string
      done:               boolean
  related_cards:          array<string>  # array de CardId
  due_date:               string | null  # ISO 8601 date "yyyy-MM-dd"
  created_at:             timestamp
  updated_at:             timestamp
```

**Nota sobre `related_cards`:** la relación es simétrica. El caso de uso `AddRelatedCard` escribe en ambos documentos en una transacción atómica.

---

### 2.3 `/areas/{areaId}`

```
areas/{areaId}
  id:           string
  name:         string
  description:  string | null
  objectives:   string | null     # texto libre — no array
  color_id:     string | null     # identificador del color del sistema (ej: "coral", "violeta")
  created_at:   timestamp
  updated_at:   timestamp
```

---

### 2.4 `/projects/{projectId}`

```
projects/{projectId}
  id:           string
  name:         string
  description:  string | null
  objectives:   string | null  # texto libre — no array
  area_id:      string         # referencia a /areas/{areaId} — obligatorio
  status:       string         # "active" | "on_hold" | "completed"
  created_at:   timestamp
  updated_at:   timestamp
```

---

### 2.5 `/epics/{epicId}`

```
epics/{epicId}
  id:           string
  space_id:     string   # referencia a /spaces/{spaceId}
  project_id:   string   # referencia a /projects/{projectId} — obligatorio
  area_id:      string   # referencia a /areas/{areaId} — obligatorio
  name:         string
  description:  string | null
  created_at:   timestamp
  updated_at:   timestamp
```

`project_id` y `area_id` son obligatorios — un Epic siempre pertenece a un Project y a un Area. Estos campos permiten consultas de Epics por Área o por Proyecto sin pasar por el Space.

---

### 2.6 `/card_indexes/{spaceId}/by_state/{stateKey}_{cardId}`

Índice ligero para consultas de tablero — obtener Cards de una columna sin leer documentos completos.

`stateKey` puede ser un `PreWorkflowStage` (`inbox`, `refinement`, `backlog`) o un `WorkflowStateId`. El ID del documento combina ambos: `{stateKey}_{cardId}`.

```
card_indexes/{spaceId}/by_state/{stateKey}_{cardId}
  card_id:       string
  title:         string
  priority:      string | null
  due_date:      string | null   # ISO 8601 date "yyyy-MM-dd"
  labels:        array<string>
  epic_id:       string | null
  updated_at:    timestamp
```

**Nota de implementación:** el documento de índice NO es una subcolección por `stateKey`. Es un documento plano dentro de la subcolección `by_state`, con ID compuesto `{stateKey}_{cardId}`. Para obtener todos los índices de una columna se consulta `by_state` filtrando por prefijo de `card_id` o iterando — en la implementación actual se itera la subcolección completa y se filtra por `stateKey` en el ID del documento.

**Se mantiene por fanout en cada `MoveCard`, `CreateCard`, `ArchiveCard`.**

---

## 3. Estrategia de escritura

### 3.1 CreateCard

Transacción atómica de 2 escrituras:

```
1. SET /cards/{cardId}
       ← documento completo

2. SET /card_indexes/{spaceId}/by_state/inbox_{cardId}
       ← índice ligero (estado inicial siempre es "inbox")
```

### 3.2 MoveCard (MoveWithinWorkflow / PromoteToWorkflow / DemoteToPreWorkflow)

Transacción atómica de hasta 3 escrituras (implementado en `save_with_index`):

```
1. SET    /cards/{cardId}
            pre_workflow_stage: <nuevo valor o null>
            workflow_state_id:  <nuevo valor o null>
            updated_at:         <now>

2. SET    /card_indexes/{spaceId}/by_state/{newStateKey}_{cardId}   ← nuevo índice

3. DELETE /card_indexes/{spaceId}/by_state/{oldStateKey}_{cardId}   ← índice antiguo
          (solo si oldStateKey != newStateKey)
```

### 3.3 ArchiveCard

Igual que MoveCard — mueve al `stateKey` del End State del workflow.

### 3.4 AddRelatedCard

Transacción atómica de 2 escrituras (relación simétrica):

```
1. UPDATE /cards/{cardId}         related_cards: arrayUnion(relatedId)
2. UPDATE /cards/{relatedId}      related_cards: arrayUnion(cardId)
```

### 3.5 DeleteArea / DeleteProject / DeleteEpic

No hay cascada automática en Firestore. El caso de uso ejecuta:

```
1. DELETE /areas/{areaId}  (o project / epic)
2. BATCH UPDATE — todas las Cards con area_id == areaId → area_id: null
```

Para volúmenes bajos (uso personal) el batch directo es suficiente.

---

## 4. Índices compuestos

Firestore requiere índices compuestos explícitos para queries con múltiples filtros y ordenación.

| Colección | Campos indexados | Consulta que lo requiere |
|---|---|---|
| `cards` | `space_id` ASC, `workflow_state_id` ASC, `updated_at` DESC | Cards por estado ordenadas por fecha |
| `cards` | `space_id` ASC, `pre_workflow_stage` ASC, `updated_at` DESC | Cards pre-workflow por columna |
| `cards` | `space_id` ASC, `area_id` ASC, `updated_at` DESC | Cards por área en un Space |
| `cards` | `space_id` ASC, `project_id` ASC, `updated_at` DESC | Cards por proyecto en un Space |
| `cards` | `space_id` ASC, `epic_id` ASC, `updated_at` DESC | Cards por epic en un Space |
| `cards` | `space_id` ASC, `priority` ASC, `due_date` ASC | Cards por prioridad con fecha límite |
| `cards` | `space_id` ASC, `due_date` ASC | Cards próximas a vencer |
| `projects` | `area_id` ASC, `status` ASC | Proyectos activos de un área |

**Los índices se definen en `firestore.indexes.json`** y se despliegan con Firebase CLI.

---

## 5. Patrones de consulta

### Vista de tablero (columnas)

Lectura en dos pasos:

```
1. GET /spaces/{spaceId}
   → obtiene WorkflowStates y su orden visual

2. GET /card_indexes/{spaceId}/by_state/{stateKey}
   → para cada columna visible (se pueden batching en paralelo)
```

El frontend agrupa los resultados por columna. Los datos ligeros del índice son suficientes para renderizar las tarjetas en el tablero.

### Detalle de Card

```
GET /cards/{cardId}   → documento completo
```

Se accede solo al abrir el detalle — no en la vista de tablero.

### Filtrado (CardFilter)

Dos estrategias según la complejidad del filtro:

**Filtro simple** (un campo indexado):
```
WHERE space_id == X AND priority IN ["high", "critical"]
```
→ Query nativa Firestore con índice compuesto.

**Filtro complejo** (múltiples campos, predicados de lista):
```
GET /cards WHERE space_id == X
→ evaluación en memoria con CardFilter.matches()
```
Para uso personal el volumen es bajo — la evaluación en memoria es aceptable y evita la explosión de índices compuestos.

### Conteo para WIP limit

```
SELECT COUNT(*) FROM /cards
WHERE space_id == X AND workflow_state_id == Y
[AND filtros adicionales de WipLimitRule]
```

Firestore soporta `count()` desde 2023 sin leer documentos completos. Se usa en `MoveCard` antes de ejecutar el movimiento.

---

## 6. Seguridad

Las reglas de seguridad de Firestore se definen en `firestore.rules` y se despliegan junto con la aplicación.

**Principios:**
- Solo usuarios autenticados via Firebase Auth pueden leer y escribir
- En v1 (single user) las reglas validan únicamente `request.auth != null`
- En v2 (multi user) se añadirá validación de `request.auth.uid` contra un campo `owner_id` en cada documento

**Consideración:** la validación de invariantes de negocio (WIP limits, transiciones) no vive en las reglas de Firestore — es responsabilidad del dominio en `sigma-core`. Las reglas de seguridad solo controlan acceso, no lógica de negocio.

---

## 7. Límites y consideraciones

### Free tier Firestore

| Operación | Límite diario | Uso estimado SIGMA |
|---|---|---|
| Reads | 50.000 | Muy por debajo — uso personal |
| Writes | 20.000 | Muy por debajo — uso personal |
| Deletes | 20.000 | Muy por debajo — uso personal |
| Storage | 1 GB | Muy por debajo |

### Límites de documento Firestore

- Tamaño máximo por documento: **1 MB**
- `workflow_states` embebidos en Space: con descripción y reglas, un Space con 20 estados ocupa ~10KB — muy por debajo del límite
- `checklist` en Card: con 100 ítems de 500 chars cada uno, ~50KB — dentro del límite

### Transacciones

- Máximo **500 documentos** por transacción — nunca alcanzado en SIGMA
- Máximo **10 writes** por segundo por documento — irrelevante para uso personal

### Evolución del esquema

Firestore no tiene schema enforcement. Los cambios de estructura se gestionan mediante:
1. Código de migración en el adaptador que normaliza documentos con campos ausentes
2. Para cambios breaking: script de migración one-shot ejecutado manualmente
