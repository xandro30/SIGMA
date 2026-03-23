# ADR-013: Estrategia de testing — BDD con behave + Gherkin

**Estado:** Aceptado
**Fecha:** 2026-03-21

## Contexto

`sigma-core` contiene el dominio puro del sistema — aggregates, value objects
y casos de uso. Es el núcleo más crítico y el que más se beneficia de una
cobertura deliberada. Se necesita una estrategia de testing que:

- Documente el comportamiento de negocio de forma legible
- Identifique los casos conflictivos sin generar tests redundantes
- Mantenga el vínculo explícito entre especificación y ejecución
- Sea sostenible para un único desarrollador

## Decisión

Feature files Gherkin ejecutados con **behave** como framework BDD.
Tests de integración con **pytest** para los adaptadores Firestore.

Los escenarios en cada feature file siguen esta taxonomía deliberada:

| Categoría | Qué cubre |
|---|---|
| **Happy path** | Flujo nominal completo — define el comportamiento esperado |
| **Validation fails** | Invariantes de VOs y Aggregates — Fail Fast en construcción |
| **Business rule violations** | Reglas de negocio: transición inválida, WIP limit, auto-referencia |
| **Edge cases** | Colección vacía, un solo elemento, idempotencia, operación repetida |
| **Boundary Value Analysis** | Rangos con límite: valor en el límite, uno dentro, uno fuera |

Lo que **no** se testea: combinaciones arbitrarias de campos válidos,
comportamientos ya cubiertos por otro escenario, internals de implementación.

## Estructura

```
sigma-core/
  tests/
    features/
      domain/
        value_objects.feature
        card_stage.feature
        card_content.feature
        space_workflow.feature
        card_filter.feature
        wip_limit.feature
      use_cases/
        create_card.feature
        move_card.feature
        promote_demote.feature
        para_assignment.feature
    steps/               ← step definitions behave
      domain/
      use_cases/
      common.py          ← steps reutilizables entre features
    integration/         ← adaptadores contra emulador Firestore (pytest)
```

Los feature files en `tests/features/` son la fuente de verdad del
comportamiento. Los step definitions en `tests/steps/` los conectan
con el código de dominio. behave los ejecuta como suite completa.

## Razonamiento

behave lee los `.feature` en Gherkin y ejecuta cada línea
`Given/When/Then` a través de step definitions — funciones Python
decoradas que mapean texto a código:

```python
@given('una Card en pre_workflow_stage = BACKLOG')
def step_impl(context):
    context.card = Card(pre_workflow_stage=PreWorkflowStage.BACKLOG, ...)

@when('se llama a move_to_workflow_state("uuid-state")')
def step_impl(context):
    context.card.move_to_workflow_state(WorkflowStateId("uuid-state"))

@then('workflow_state_id es "uuid-state"')
def step_impl(context):
    assert context.card.workflow_state_id == WorkflowStateId("uuid-state")
```

Los beneficios concretos que justifican esta elección:

- El `.feature` y el test están **explícitamente vinculados** — no hay
  ambigüedad entre especificación e implementación
- La salida de behave muestra los **escenarios por nombre**, más legible
  que nombres de funciones pytest en la revisión diaria
- La disciplina de escribir step definitions obliga a que cada línea
  Gherkin sea **ejecutable** — los `.feature` no pueden quedar
  desactualizados sin que los tests fallen
- Los step definitions son **reutilizables** entre escenarios — el paso
  `Given una Card en pre_workflow_stage = BACKLOG` se escribe una vez
  y lo usan todos los escenarios que lo necesiten

Nota: **Cucumber no aplica aquí** — es el framework BDD equivalente para
Ruby, Java y JavaScript. behave es su equivalente directo para Python.

## Alternativas consideradas

- **Solo pytest sin Gherkin**: tests rápidos pero sin vínculo explícito
  entre especificación y ejecución. Los escenarios de negocio quedan
  como comentarios que pueden desincronizarse del código. Descartado.
- **Feature files sin ejecutar (solo documentación)**: los `.feature`
  quedan desactualizados inevitablemente si no hay nada que los valide.
  Descartado.
- **pytest con comentarios Given/When/Then inline**: mismo resultado
  visual pero sin la disciplina que impone behave ni la reutilización
  de steps. Descartado.

## Consecuencias

- Los feature files se escriben **antes** que el código de producción
  (BDD-first) — son la especificación ejecutable
- Todo escenario en un feature file tiene su step definition correspondiente
- Los step definitions comunes se extraen a `steps/common.py` para
  evitar duplicación entre features
- La cobertura se mide por comportamientos relevantes, no por líneas
- Los tests de dominio son unitarios puros — sin mocks, sin base de datos.
  Solo objetos de dominio en memoria
- La integración con Firestore se cubre en `tests/integration/` con el
  emulador local de Firestore usando pytest
- Ejecución: `behave tests/features/` para el dominio,
  `uv run pytest tests/integration/` para los adaptadores
