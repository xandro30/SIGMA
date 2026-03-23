# ADR-006: Bounded Context único para v1 — TaskManagement

**Estado:** Propuesto
**Fecha:** 2026-03-21

## Contexto

SIGMA gestiona tareas (creación, estados, clasificación) y en
el futuro necesitará planificación temporal (timeboxing,
estimaciones, tracking). Son responsabilidades distintas que
podrían justificar Bounded Contexts separados.

## Decisión

v1 implementa un único Bounded Context: `TaskManagement`.
El contexto `Planning` (timeboxing, estimaciones, tracking)
queda diferido a v2.

## Razonamiento

En v1 no existe ningún flujo que cruce los dos contextos —
no hay caso de uso que necesite datos de Planning para
completar una operación de TaskManagement o viceversa.
Introducir dos contextos sin una frontera real añade
complejidad accidental sin beneficio tangible.

La regla de separación aplica cuando existe un lenguaje
ubicuo distinto o invariantes que no se pueden mantener
en el mismo modelo. Esa condición no se cumple en v1.

## Alternativas consideradas

- **Dos Bounded Contexts desde el inicio (TaskManagement +
  Planning)**: correcto a largo plazo pero prematuro. Sin
  casos de uso reales que crucen la frontera es imposible
  definirla bien. Descartado — YAGNI.
- **Un único modelo plano sin contextos**: no aplica
  arquitectura hexagonal. Descartado.

## Consecuencias

- `sigma-core` modela únicamente TaskManagement en v1
- Cuando se implemente Planning se creará un contexto
  separado con su propio modelo y sus propios puertos
- La frontera entre contextos se definirá cuando existan
  casos de uso que la crucen, no antes
- No hay anti-corruption layer necesario en v1
