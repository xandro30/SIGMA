Feature: CreateCard — caso de uso de creación de Card

  CreateCard crea una nueva Card en un Space.
  Por defecto entra en INBOX. Acepta un stage inicial opcional.
  El Space debe existir.

  Background:
    Given un Space "Work" existente con estado Start "TO DO" y End "DONE"

  # ─── Happy path ───────────────────────────────────────────────────

  Scenario: Crear Card con título válido entra en INBOX por defecto
    When se ejecuta CreateCard con space_id="Work" y title="Revisar logs"
    Then se crea una Card con título "Revisar logs"
    And la Card está en pre_workflow_stage = INBOX
    And la Card tiene un CardId generado
    And la Card está persistida en el repositorio

  Scenario: Crear Card con todos los campos opcionales
    When se ejecuta CreateCard con:
      | space_id     | "Work"              |
      | title        | "Implementar login" |
      | description  | "Descripción..."    |
      | priority     | high                |
      | area_id      | "uuid-area"         |
      | project_id   | "uuid-project"      |
      | epic_id      | "uuid-epic"         |
      | due_date     | 2026-03-28          |
      | labels       | ["#SecOps"]         |
      | topics       | ["IAM"]             |
    Then la Card se crea con todos esos valores
    And la Card está en pre_workflow_stage = INBOX

  Scenario: Crear Card con initial_stage = REFINEMENT
    When se ejecuta CreateCard con title="Idea sin depurar" y initial_stage = REFINEMENT
    Then la Card está en pre_workflow_stage = REFINEMENT

  Scenario: Crear Card con initial_stage = WorkflowStateId (caso urgente)
    When se ejecuta CreateCard con title="Incidencia crítica" e initial_stage = "uuid-todo"
    Then la Card está en workflow_state_id = "uuid-todo"
    And pre_workflow_stage es None

  # ─── Validation fails ────────────────────────────────────────────

  Scenario: Crear Card con título vacío es rechazado
    When se ejecuta CreateCard con title=""
    Then se lanza un ValueError antes de persistir
    And no se escribe nada en el repositorio

  Scenario: Crear Card en Space inexistente es rechazado
    When se ejecuta CreateCard con space_id="uuid-inexistente"
    Then se lanza un SpaceNotFoundError
    And no se escribe nada en el repositorio

  Scenario: Crear Card con WorkflowStateId que no existe en el Space es rechazado
    When se ejecuta CreateCard con initial_stage = "uuid-estado-que-no-existe"
    Then se lanza un StateNotFoundError
    And no se escribe nada en el repositorio

  Scenario: Crear Card con URL inválida en urls es rechazado
    When se ejecuta CreateCard con urls = ["no-es-una-url"]
    Then se lanza un ValueError antes de persistir

  # ─── Edge cases ──────────────────────────────────────────────────

  Scenario: Dos Cards creadas con el mismo título tienen IDs distintos
    When se ejecutan dos CreateCard con el mismo title="Tarea duplicada"
    Then se crean dos Cards con CardId distintos

  Scenario: Card creada tiene created_at y updated_at iguales en el momento de creación
    When se ejecuta CreateCard con title="Tarea nueva"
    Then created_at y updated_at tienen el mismo valor
