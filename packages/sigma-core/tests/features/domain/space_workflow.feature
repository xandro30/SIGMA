Feature: Space Workflow — invariantes y configuración del workflow

  Space es el Aggregate Root que protege la coherencia del workflow.
  Sus invariantes garantizan que el workflow siempre es navegable.

  # ─── Invariantes de creación ─────────────────────────────────────

  Scenario: Space válido con workflow completo se crea correctamente
    Given un Space con un estado Start y un estado End
    When se valida el Space
    Then el Space es válido

  Scenario: Space sin estado Start es rechazado
    Given un Space con solo un estado End y ningún estado Start
    When se valida el Space
    Then se lanza un InvalidWorkflowError indicando Start ausente

  Scenario: Space sin estado End es rechazado
    Given un Space con solo un estado Start y ningún estado End
    When se valida el Space
    Then se lanza un InvalidWorkflowError indicando End ausente

  Scenario: Space con dos estados Start es rechazado
    Given un Space con dos estados marcados como is_start = True
    When se valida el Space
    Then se lanza un InvalidWorkflowError indicando Start duplicado

  Scenario: Space con transición a estado inexistente es rechazado
    Given un Space con un estado Start que apunta a "uuid-inexistente" en allowed_transitions
    When se valida el Space
    Then se lanza un InvalidWorkflowError indicando referencia inválida

  # ─── add_state ───────────────────────────────────────────────────

  Scenario: Añadir un estado intermedio a un workflow existente
    Given un Space con estado Start "TO DO" y estado End "DONE"
    When se llama a add_state con un estado "WIP" de orden 2
    Then el Space tiene 3 estados
    And los estados están ordenados por order

  Scenario: Añadir un estado con ID duplicado es rechazado
    Given un Space con un estado de ID "uuid-state"
    When se intenta añadir otro estado con el mismo ID "uuid-state"
    Then se lanza un DuplicateStateError

  Scenario: Añadir un estado con transición a estado inexistente es rechazado
    Given un Space con estado Start y End
    When se intenta añadir un estado cuyas allowed_transitions apuntan a un ID inexistente
    Then se lanza un InvalidWorkflowError

  # ─── remove_state ────────────────────────────────────────────────

  Scenario: Eliminar un estado intermedio del workflow
    Given un Space con estados Start, WIP y End
    When se llama a remove_state con el ID de WIP
    Then el Space tiene 2 estados: Start y End

  Scenario: Eliminar el estado Start es rechazado
    Given un Space con estado Start y End
    When se intenta eliminar el estado Start
    Then se lanza un InvalidWorkflowError indicando que Start no se puede eliminar

  Scenario: Eliminar el estado End es rechazado
    Given un Space con estado Start y End
    When se intenta eliminar el estado End
    Then se lanza un InvalidWorkflowError indicando que End no se puede eliminar

  Scenario: Eliminar un estado inexistente no lanza error
    Given un Space con estado Start y End
    When se llama a remove_state con un ID que no existe
    Then se lanza un StateNotFoundError

  # ─── is_valid_transition ─────────────────────────────────────────

  Scenario: Transición permitida explícitamente es válida
    Given un Space con estado "TO DO" cuyas allowed_transitions incluyen "WIP"
    When se llama a is_valid_transition("TO DO", "WIP")
    Then retorna True

  Scenario: Transición no incluida en allowed_transitions es inválida
    Given un Space con estado "TO DO" cuyas allowed_transitions incluyen solo "WIP"
    When se llama a is_valid_transition("TO DO", "DONE")
    Then retorna False

  Scenario: Transición desde estado con allowed_transitions vacío es siempre válida
    Given un Space con estado "TO DO" cuyas allowed_transitions están vacías
    When se llama a is_valid_transition("TO DO", "DONE")
    Then retorna True

  Scenario: Transición desde estado inexistente retorna False
    Given un Space con estado Start y End
    When se llama a is_valid_transition("uuid-inexistente", "uuid-end")
    Then retorna False

  # ─── get_start_state / get_end_state ─────────────────────────────

  Scenario: get_start_state retorna el estado marcado como Start
    Given un Space con estado Start "TO DO" y End "DONE"
    When se llama a get_start_state()
    Then retorna el estado con nombre "TO DO"

  Scenario: get_end_state retorna el estado marcado como End
    Given un Space con estado Start "TO DO" y End "DONE"
    When se llama a get_end_state()
    Then retorna el estado con nombre "DONE"

  # ─── Edge cases ──────────────────────────────────────────────────

  Scenario: Space con workflow de un único estado que es Start y End a la vez
    Given un Space con un estado marcado is_start = True y is_end = True simultáneamente
    When se valida el Space
    Then el Space es válido
    And get_start_state() y get_end_state() retornan el mismo estado
