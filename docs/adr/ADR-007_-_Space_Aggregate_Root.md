# ADR-007: Space como Aggregate Root del Workflow

**Estado:** Propuesto
**Fecha:** 2026-03-21

## Contexto

El workflow de SIGMA es configurable por el usuario: cada
Space define sus propios estados, sus transiciones permitidas
y sus WIP limits. Estos elementos son interdependientes —
una transición no puede apuntar a un estado que no existe
en el mismo Space.

## Decisión

`Space` es el Aggregate Root que contiene y protege la
coherencia del workflow. `WorkflowState` es una entidad
que solo existe dentro de `Space` y no tiene identidad
fuera de él.

```
Space (AR)
  ├── id: SpaceId
  ├── name: str
  └── workflow_states: list[WorkflowState]
        ├── id: WorkflowStateId
        ├── name: str
        ├── order: int
        ├── is_start: bool
        ├── is_end: bool
        ├── wip_limit: int | None
        └── allowed_transitions: frozenset[WorkflowStateId]
```

## Razonamiento

Los invariantes del workflow son internos a Space:
- Debe existir exactamente un estado con `is_start = True`
- Debe existir exactamente un estado con `is_end = True`
- Toda `WorkflowStateId` en `allowed_transitions` debe
  existir en el mismo Space

Estos invariantes solo se pueden garantizar si Space controla
todas las mutaciones sobre sus `WorkflowState`. Ninguna
entidad externa puede añadir, eliminar o modificar estados
sin pasar por el AR.

## Alternativas consideradas

- **WorkflowState como AR independiente**: imposible garantizar
  los invariantes de transiciones sin cargar el Space completo.
  Descartado.
- **Workflow como AR separado referenciado por Space**: añade
  un nivel de indirección sin beneficio. El workflow no tiene
  ciclo de vida independiente al Space. Descartado.

## Consecuencias

- Para validar una transición de Card, el caso de uso carga
  el Space por su `space_id` y llama a `space.validate_transition()`
- Eliminar un WorkflowState requiere verificar que ningún
  Card activo lo referencia — responsabilidad del caso de uso
- El Space completo se carga en cada validación de transición;
  aceptable dado el volumen de uso personal
