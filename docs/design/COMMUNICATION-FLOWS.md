# COMMUNICATION-FLOWS.md

## SIGMA — Flujos de comunicación

**Versión:** 1.0
**Fecha:** 2026-03-21

---

## Índice

1. [Crear Card](#1-crear-card)
2. [Mover Card dentro del Workflow](#2-mover-card-dentro-del-workflow)
3. [Promover Card al Workflow](#3-promover-card-al-workflow)
4. [WIP limit excedido](#4-wip-limit-excedido)
5. [Vista de tablero con filtro](#5-vista-de-tablero-con-filtro)
6. [Crear Space con Workflow](#6-crear-space-con-workflow)
7. [Operación desde Claude (MCP)](#7-operación-desde-claude-mcp)
8. [Autenticación](#8-autenticación)

---

## 1. Crear Card

Caso base: Card nueva desde el tablero, entra en INBOX.

```mermaid
sequenceDiagram
    actor U as Usuario
    participant W as sigma-web
    participant R as sigma-rest
    participant UC as CreateCard
    participant D as Card (domain)
    participant CR as CardRepository
    participant DB as Firestore

    U->>W: Click [+ Card] o [+] en columna INBOX
    W->>W: Muestra formulario inline (título, stage inicial)
    U->>W: Introduce título y confirma
    W->>R: POST /spaces/{spaceId}/cards\n{ title, initial_stage: "inbox" }
    R->>R: Valida request (título no vacío, spaceId válido)
    R->>UC: CreateCard(space_id, title, initial_stage=INBOX)
    UC->>D: Card(id=CardId.generate(), title=CardTitle(title),\npre_workflow_stage=INBOX, ...)
    D->>D: __post_init__ — valida invariantes
    UC->>CR: save(card)
    CR->>DB: Transaction:\n  SET /cards/{cardId}\n  SET /card_indexes/{spaceId}/by_state/inbox/{cardId}
    DB-->>CR: OK
    CR-->>UC: OK
    UC-->>R: card_id
    R-->>W: 201 Created { card_id, ... }
    W->>W: Añade Card al tablero en columna INBOX
    W-->>U: Tarjeta visible en INBOX
```

---

## 2. Mover Card dentro del Workflow

Incluye validación de transición y WIP limits.

```mermaid
sequenceDiagram
    actor U as Usuario
    participant W as sigma-web
    participant R as sigma-rest
    participant UC as MoveWithinWorkflow
    participant SR as SpaceRepository
    participant CR as CardRepository
    participant DB as Firestore

    U->>W: Drag & drop Card de [TO DO] a [WIP]
    W->>W: Optimistic update — mueve Card visualmente
    W->>R: PATCH /cards/{cardId}/move\n{ target_state_id }

    R->>UC: MoveWithinWorkflow(card_id, target_state_id)

    UC->>SR: get_by_id(space_id)
    SR->>DB: GET /spaces/{spaceId}
    DB-->>SR: Space document
    SR-->>UC: Space

    UC->>UC: space.is_valid_transition(current_state_id, target_state_id)
    Note over UC: Si allowed_transitions vacío → válido\nSi no está en la lista → InvalidTransitionError

    UC->>CR: count_by_workflow_state(space_id, target_state_id, wip_filter)
    CR->>DB: COUNT /cards WHERE space_id=X AND workflow_state_id=Y
    DB-->>CR: count = 2

    UC->>UC: Evalúa WipLimitRules del estado destino\ncount(2) < max_cards(3) → OK

    UC->>CR: get_by_id(card_id)
    CR->>DB: GET /cards/{cardId}
    DB-->>CR: Card document
    CR-->>UC: Card

    UC->>UC: card.move_to_workflow_state(target_state_id)

    UC->>CR: save(card)
    CR->>DB: Transaction:\n  UPDATE /cards/{cardId} — workflow_state_id, updated_at\n  SET /card_indexes/{spaceId}/by_state/{newState}/{cardId}\n  DELETE /card_indexes/{spaceId}/by_state/{oldState}/{cardId}
    DB-->>CR: OK

    UC-->>R: OK
    R-->>W: 200 OK
    W->>W: Confirma optimistic update
    W-->>U: Card en columna WIP
```

---

## 4. WIP limit excedido

El servidor rechaza el movimiento y el cliente revierte el optimistic update.

```mermaid
sequenceDiagram
    actor U as Usuario
    participant W as sigma-web
    participant R as sigma-rest
    participant UC as MoveWithinWorkflow
    participant CR as CardRepository
    participant DB as Firestore

    U->>W: Drag & drop Card a [WIP] (ya tiene 3 cards)
    W->>W: Optimistic update — mueve Card visualmente
    W->>R: PATCH /cards/{cardId}/move\n{ target_state_id }

    R->>UC: MoveWithinWorkflow(card_id, target_state_id)
    UC->>CR: count_by_workflow_state(space_id, target_state_id, filter)
    CR->>DB: COUNT...
    DB-->>CR: count = 3

    UC->>UC: count(3) >= max_cards(3) → WipLimitExceededError
    UC-->>R: WipLimitExceededError

    R-->>W: 422 Unprocessable Entity\n{ error: "wip_limit_exceeded",\n  state: "WIP", limit: 3, current: 3 }

    W->>W: Revierte optimistic update\nCard vuelve a columna original
    W-->>U: Toast: "WIP limit alcanzado (3/3). Completa una tarea antes de añadir más."
```

---

## 3. Promover Card al Workflow

Card en BACKLOG → primer estado del workflow (o estado de entrada urgente).

```mermaid
sequenceDiagram
    actor U as Usuario
    participant W as sigma-web
    participant R as sigma-rest
    participant UC as PromoteToWorkflow
    participant SR as SpaceRepository
    participant CR as CardRepository
    participant DB as Firestore

    U->>W: Drag & drop Card de [BACKLOG] a [TO DO]
    W->>R: PATCH /cards/{cardId}/promote\n{ target_state_id }

    R->>UC: PromoteToWorkflow(card_id, target_state_id)

    UC->>SR: get_by_id(space_id)
    SR->>DB: GET /spaces/{spaceId}
    DB-->>UC: Space

    UC->>UC: Verifica target_state_id existe en Space
    UC->>UC: Evalúa WipLimitRules del estado destino

    UC->>CR: get_by_id(card_id)
    CR->>DB: GET /cards/{cardId}
    DB-->>UC: Card

    UC->>UC: Verifica card.is_in_pre_workflow() == True
    UC->>UC: card.move_to_workflow_state(target_state_id)

    UC->>CR: save(card)
    CR->>DB: Transaction:\n  UPDATE /cards/{cardId}\n  SET /card_indexes/.../by_state/{newState}/{cardId}\n  DELETE /card_indexes/.../by_state/backlog/{cardId}
    DB-->>CR: OK

    R-->>W: 200 OK
    W-->>U: Card en columna TO DO
```

---

## 5. Vista de tablero con filtro

Carga inicial del tablero y aplicación de filtro.

```mermaid
sequenceDiagram
    actor U as Usuario
    participant W as sigma-web
    participant R as sigma-rest
    participant DB as Firestore

    U->>W: Navega a Board (Space: Work)

    par Carga en paralelo
        W->>R: GET /spaces/{spaceId}
        R->>DB: GET /spaces/{spaceId}
        DB-->>R: Space + WorkflowStates
        R-->>W: Space (para renderizar columnas y orden)
    and
        W->>R: GET /spaces/{spaceId}/board
        R->>DB: GET /card_indexes/{spaceId}/by_state/* (batch)
        DB-->>R: Card indexes de todas las columnas
        R-->>W: Cards agrupadas por columna (datos ligeros)
    end

    W->>W: Renderiza tablero con columnas y tarjetas
    W-->>U: Tablero visible

    U->>W: Activa filtro: Prioridad = HIGH, CRITICAL
    W->>W: Aplica filtro en cliente sobre cards ya cargadas
    W-->>U: Tablero muestra solo cards HIGH y CRITICAL

    Note over W: Para filtros complejos (topics, labels)\nse hace nueva request al servidor
    W->>R: GET /spaces/{spaceId}/cards?priority=high,critical&topic=IAM
    R->>DB: Query con índices compuestos
    DB-->>R: Cards filtradas
    R-->>W: Cards filtradas
    W->>W: Actualiza vista
    W-->>U: Tablero filtrado
```

---

## 6. Crear Space con Workflow

Configuración inicial de un nuevo Space.

```mermaid
sequenceDiagram
    actor U as Usuario
    participant W as sigma-web
    participant R as sigma-rest
    participant UC_S as CreateSpace
    participant UC_WS as AddWorkflowState
    participant SR as SpaceRepository
    participant DB as Firestore

    U->>W: Click [+ Space]
    W-->>U: Formulario: nombre del Space
    U->>W: Introduce nombre "Work" y confirma

    W->>R: POST /spaces { name: "Work" }
    R->>UC_S: CreateSpace("Work")
    UC_S->>SR: save(space)
    SR->>DB: SET /spaces/{spaceId} (workflow_states: [])
    DB-->>SR: OK
    R-->>W: 201 Created { space_id }

    W-->>U: Space creado. Redirige a ⚙ Space settings

    loop Para cada estado del workflow
        U->>W: Añade estado (nombre, tipo, WIP limit, transiciones)
        W->>R: POST /spaces/{spaceId}/workflow-states\n{ name, is_start, is_end, wip_limit_rules, allowed_transitions }
        R->>UC_WS: AddWorkflowState(space_id, state_data)
        UC_WS->>SR: get_by_id(space_id)
        SR->>DB: GET /spaces/{spaceId}
        DB-->>UC_WS: Space
        UC_WS->>UC_WS: space.add_state(state) — valida invariantes
        UC_WS->>SR: save(space)
        SR->>DB: UPDATE /spaces/{spaceId}
        R-->>W: 200 OK
        W-->>U: Estado añadido al workflow
    end

    W-->>U: Workflow configurado. Redirige a Board.
```

---

## 7. Operación desde Claude (MCP)

Claude crea una Card y la promueve al workflow en una conversación.

```mermaid
sequenceDiagram
    actor Dev as Desarrollador
    participant C as Claude
    participant M as sigma-mcp
    participant UC_C as CreateCard
    participant UC_P as PromoteToWorkflow
    participant SR as SpaceRepository
    participant CR as CardRepository
    participant DB as Firestore

    Dev->>C: "Crea una tarea urgente para revisar\nlos WIP limits del workflow"

    C->>M: tool: create_card\n{ space_id, title: "Revisar WIP limits del workflow",\n  priority: "high" }

    M->>UC_C: CreateCard(space_id, title, priority=HIGH)
    UC_C->>CR: save(card) — card en INBOX
    CR->>DB: Transaction: SET /cards + SET /card_indexes/.../inbox
    DB-->>CR: OK
    UC_C-->>M: card_id

    C->>M: tool: promote_card_to_workflow\n{ card_id, target_state_id: <start_state_id> }

    M->>UC_P: PromoteToWorkflow(card_id, target_state_id)
    UC_P->>SR: get_by_id(space_id)
    SR->>DB: GET /spaces/{spaceId}
    DB-->>UC_P: Space
    UC_P->>UC_P: Valida estado destino y WIP limits
    UC_P->>CR: get_by_id(card_id)
    CR->>DB: GET /cards/{cardId}
    DB-->>UC_P: Card
    UC_P->>UC_P: card.move_to_workflow_state(start_state_id)
    UC_P->>CR: save(card)
    CR->>DB: Transaction: UPDATE card + fanout card_indexes
    DB-->>CR: OK
    UC_P-->>M: OK

    M-->>C: { card_id, state: "TO DO", title: "..." }
    C-->>Dev: "Creé la tarea 'Revisar WIP limits del workflow'\ncon prioridad HIGH y la moví directamente a TO DO."
```

---

## 8. Autenticación

Flujo de login inicial — Firebase Auth con Google.

```mermaid
sequenceDiagram
    actor U as Usuario
    participant W as sigma-web
    participant FA as Firebase Auth
    participant R as sigma-rest

    U->>W: Accede a la PWA
    W->>W: Comprueba sesión local (Firebase SDK)
    W-->>U: Pantalla de login (sin sesión activa)

    U->>W: Click [Continuar con Google]
    W->>FA: signInWithPopup(GoogleAuthProvider)
    FA-->>W: ID Token (JWT)

    W->>W: Almacena sesión en Firebase SDK
    W-->>U: Redirige al tablero

    Note over W,R: Cada request REST incluye el ID Token en header
    W->>R: GET /spaces\nAuthorization: Bearer <ID Token>
    R->>FA: Verifica ID Token (firebase-admin SDK)
    FA-->>R: Token válido, uid extraído
    R->>R: Procesa request con uid como contexto
    R-->>W: Respuesta con datos del usuario
```
