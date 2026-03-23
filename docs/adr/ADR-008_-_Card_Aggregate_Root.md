# ADR-008: Card como Aggregate Root independiente

**Estado:** Propuesto
**Fecha:** 2026-03-21

## Contexto

Una Card pertenece semánticamente a un Space — no tiene
sentido sin él. Sin embargo, la forma en que se modela esa
pertenencia (referencia por ID vs. contención estructural)
tiene implicaciones profundas en el diseño.

## Decisión

`Card` es un Aggregate Root independiente. Conoce su Space
a través de `space_id` (referencia por ID), no contiene
ni navega el objeto `Space`.

## Razonamiento

Un Aggregate Root define un límite de consistencia
transaccional. La pregunta es: ¿qué invariantes necesitan
mantenerse dentro de una sola transacción?

**Invariantes de Card** (solo necesitan datos de Card):
- El título no puede estar vacío
- Máximo 5 labels
- Exactamente uno de `pre_workflow_stage` o
  `workflow_state_id` debe estar activo
- `blocked_from_stage` solo puede estar activo si el card
  está en un estado de bloqueo

**Invariantes que cruzan Card y Space** (solo en MoveCard):
- La transición entre estados debe ser válida según el workflow
- El estado destino no puede superar su WIP limit

Estos invariantes cruzados se resuelven en el caso de uso
`MoveCard`, que carga ambos ARs en la misma operación. No
requieren que Card contenga a Space.

Si Card viviera dentro de Space, crear o editar una tarjeta
requeriría cargar el Space completo con todos sus estados.
Eso es acoplamiento innecesario y viola el principio de
menor sorpresa.

## Alternativas consideradas

- **Card dentro de Space**: garantiza pertenencia estructural
  pero carga el aggregate completo para cualquier operación
  sobre Card. Escala mal y viola SRP. Descartado.
- **Card sin referencia a Space**: Card completamente autónomo.
  Pierde la capacidad de navegar hacia el workflow. Descartado.

## Consecuencias

- `CardRepository` y `SpaceRepository` son puertos separados
- El caso de uso `MoveCard` carga Space + Card y coordina
  la validación
- Cards se pueden consultar y modificar sin cargar el Space,
  excepto en operaciones de transición de estado
- La pertenencia semántica Card → Space se expresa a través
  de `space_id`, no de contención estructural
