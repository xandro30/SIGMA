# ADR-009: PreWorkflowStage como enum fijo de sistema

**Estado:** Propuesto
**Fecha:** 2026-03-21

## Contexto

Antes de entrar al workflow configurable, las Cards pasan
por etapas previas: captura inicial, refinamiento y espera
para iniciar. Estas etapas podrían modelarse como estados
más del workflow o como un concepto separado y fijo.

## Decisión

`PreWorkflowStage` es un enum fijo de sistema con tres
valores. No es configurable por el usuario.

```python
class PreWorkflowStage(str, Enum):
    INBOX      = "inbox"       # idea capturada, sin depurar
    REFINEMENT = "refinement"  # creada, falta información
    BACKLOG    = "backlog"     # lista para iniciar el workflow
```

Una Card en pre-workflow tiene `pre_workflow_stage` activo
y `workflow_state_id` nulo. Al mover al workflow, se invierte.

## Razonamiento

Estas tres etapas tienen semántica universal en metodologías
de gestión de tareas — no son específicas del flujo de trabajo
del usuario. Representan el ciclo de vida previo al trabajo
activo, no el trabajo en sí.

Modelarlas como `WorkflowState` configurables permitiría al
usuario eliminarlas o renombrarlas, rompiendo la semántica
que el sistema necesita para su comportamiento interno
(por ejemplo, las Cards nuevas siempre aterrizan en INBOX).

Mantenerlas como enum fijo garantiza que el sistema siempre
tiene un punto de entrada conocido independientemente de
cómo configure el usuario su workflow.

## Alternativas consideradas

- **Inbox/Refinement/Backlog como WorkflowStates configurables**:
  el usuario podría eliminarlos o alterar su semántica. El
  sistema perdería el punto de entrada garantizado. Descartado.
- **Solo Inbox como fijo, Refinement y Backlog configurables**:
  introduce inconsistencia en el modelo. Descartado.

## Consecuencias

- Cards nuevas siempre se crean en `PreWorkflowStage.INBOX`
- La transición de pre-workflow a workflow es una operación
  distinguida: `PromoteToWorkflow(card_id, target_state_id)`
- No existe transición directa entre `WorkflowState` y
  `PreWorkflowStage` — una Card puede volver a BACKLOG
  solo de forma explícita (operación `DemoteToBacklog`)
- El frontend siempre puede renderizar las tres columnas
  pre-workflow sin consultar la configuración del Space
