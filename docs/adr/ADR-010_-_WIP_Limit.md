# ADR-010: WIP limit validado en capa de caso de uso

**Estado:** Propuesto
**Fecha:** 2026-03-21

## Contexto

Los WorkflowStates pueden tener un WIP limit — un máximo
de Cards simultáneas en ese estado. Cuando se mueve una
Card a un estado con WIP limit, el sistema debe verificar
que no se supere ese límite. La pregunta es dónde vive
esa validación.

## Decisión

La validación del WIP limit es responsabilidad del caso de
uso `MoveCard`, no del Aggregate Root `Card` ni de `Space`.

```
MoveCard(card_id, target_state_id):
  1. Cargar Space → obtener WorkflowState destino y su wip_limit
  2. Si wip_limit existe → consultar CardRepository.count_by_state()
  3. Si count >= wip_limit → lanzar WipLimitExceededError
  4. Cargar Card → ejecutar card.move_to(target_state_id)
  5. Persistir Card
```

## Razonamiento

El WIP limit no es un invariante interno de Card — una Card
no puede saber cuántas otras Cards hay en un estado sin
acceder al repositorio. Inyectar el repositorio dentro de
un Aggregate Root viola el principio de que los ARs son
objetos de dominio puros sin dependencias de infraestructura.

Tampoco es un invariante de Space — Space conoce las reglas
(el límite definido) pero no el estado actual (cuántas Cards
hay ahora). Space es un objeto de configuración, no de
conteo en tiempo real.

El caso de uso es el lugar correcto: coordina la consulta
al repositorio, la validación contra la regla del Space, y
la mutación del Card en una sola operación coherente.

## Alternativas consideradas

- **Validar en Card.move_to() inyectando un servicio de
  conteo**: introduce dependencias de infraestructura en el
  AR. Viola la pureza del dominio. Descartado.
- **Validar en Space con un método que reciba el conteo como
  parámetro**: posible, pero añade complejidad sin beneficio
  real. El caso de uso sigue siendo el coordinador. Descartado.

## Consecuencias

- `CardRepository` expone `count_by_workflow_state(state_id)`
- `Card.move_to()` permanece puro — solo valida que la
  transición es permitida según el workflow, no el conteo
- El WIP limit puede cambiar en Space sin afectar a Card
- Los tests del caso de uso `MoveCard` cubren el escenario
  de WIP limit excedido con un mock del repositorio
