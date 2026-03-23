# ADR-012: Column es concepto de presentación, no entidad de dominio

**Estado:** Propuesto
**Fecha:** 2026-03-21

## Contexto

En la interfaz visual de SIGMA, las Cards se muestran
agrupadas en columnas — una columna por estado. En el
modelo anterior (pre-refactoring) Column era una entidad
de dominio con su propia colección en Firestore. Con la
introducción de WorkflowState configurable y PreWorkflowStage
fijo, es necesario revisar ese rol.

## Decisión

`Column` no es una entidad de dominio ni tiene representación
en la base de datos. Es un concepto de presentación que el
frontend construye componiendo `PreWorkflowStage` y
`WorkflowState`.

```
Vista de columnas (frontend):
  [INBOX] [REFINEMENT] [BACKLOG]  ←  PreWorkflowStage (enum fijo)
  [Start] [...estados...] [End]   ←  WorkflowState (configurables)
```

## Razonamiento

Una Column no tiene comportamiento ni invariantes propios.
Su única función es agrupar Cards visualmente por su estado
actual. Esa agrupación se puede derivar en el momento de
la consulta directamente desde los datos que ya existen en
Card (`pre_workflow_stage` y `workflow_state_id`).

Mantener Column como entidad implicaría sincronizar tres
fuentes de verdad (Card, WorkflowState, Column) en cada
operación de movimiento. Eso es complejidad accidental.

La consulta `GetCardsByState` devuelve Cards filtradas por
estado; el frontend decide cómo renderizarlas en columnas.

## Alternativas consideradas

- **Column como entidad con colección propia en Firestore**:
  requiere fanout en cada movimiento de Card para mantener
  sincronía. Añade complejidad operacional sin lógica de
  negocio. Descartado.
- **Column como entidad en memoria (sin persistencia)**:
  construcción en cada request. Equivalente a la decisión
  tomada pero con un objeto innecesario. Descartado.

## Consecuencias

- La colección `/columns` y `/columns_cards` definidas en
  ADR-003 quedan obsoletas y se eliminan del modelo de
  persistencia (ADR-003 requiere actualización)
- El orden visual de las columnas pre-workflow es fijo
  (INBOX → REFINEMENT → BACKLOG)
- El orden de las columnas del workflow se deriva del campo
  `order` de cada `WorkflowState`
- El frontend construye la vista de tablero con una sola
  consulta: estados del Space + Cards del Space agrupadas
  por estado
