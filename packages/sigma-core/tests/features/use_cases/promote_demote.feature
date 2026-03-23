Feature: PromoteToWorkflow y DemoteToPreWorkflow

  PromoteToWorkflow mueve una Card del pre-workflow al workflow.
  DemoteToPreWorkflow devuelve una Card del workflow al pre-workflow.
  Ambos respetan WIP limits en la operación de promoción.

  Background:
    Given un Space "Work" con workflow:
      | nombre | is_start | is_end | wip_limit |
      | TO DO  | true     | false  | —         |
      | WIP    | false    | false  | 2         |
      | DONE   | false    | true   | —         |

  # ─── PromoteToWorkflow — Happy path ──────────────────────────────

  Scenario: Promover Card desde BACKLOG al Start State sin especificar target
    Given una Card en pre_workflow_stage = BACKLOG
    When se ejecuta PromoteToWorkflow sin target_state_id
    Then la Card tiene workflow_state_id = "TO DO" (Start State)
    And pre_workflow_stage es None
    And el card_index se actualiza: nuevo en TO DO, eliminado de BACKLOG

  Scenario: Promover Card desde BACKLOG a estado específico
    Given una Card en pre_workflow_stage = BACKLOG
    When se ejecuta PromoteToWorkflow con target_state_id = "WIP"
    Then la Card tiene workflow_state_id = "WIP"

  Scenario: Promover Card desde INBOX (caso urgente)
    Given una Card en pre_workflow_stage = INBOX
    When se ejecuta PromoteToWorkflow con target_state_id = "TO DO"
    Then la Card tiene workflow_state_id = "TO DO"

  Scenario: Promover Card desde REFINEMENT
    Given una Card en pre_workflow_stage = REFINEMENT
    When se ejecuta PromoteToWorkflow con target_state_id = "TO DO"
    Then la Card tiene workflow_state_id = "TO DO"

  # ─── PromoteToWorkflow — Business rule violations ────────────────

  Scenario: Promover a estado con WIP limit alcanzado es rechazado
    Given una Card en pre_workflow_stage = BACKLOG
    And hay 2 Cards en WIP (límite = 2)
    When se ejecuta PromoteToWorkflow con target_state_id = "WIP"
    Then se lanza un WipLimitExceededError
    And la Card sigue en pre_workflow_stage = BACKLOG

  Scenario: Promover Card que ya está en el workflow es rechazado
    Given una Card en workflow_state_id = "TO DO"
    When se ejecuta PromoteToWorkflow
    Then se lanza un InvalidTransitionError indicando que la Card ya está en el workflow

  # ─── PromoteToWorkflow — Validation fails ────────────────────────

  Scenario: Promover a estado inexistente en el Space es rechazado
    Given una Card en pre_workflow_stage = BACKLOG
    When se ejecuta PromoteToWorkflow con target_state_id = "uuid-inexistente"
    Then se lanza un StateNotFoundError

  Scenario: Promover Card inexistente es rechazado
    When se ejecuta PromoteToWorkflow con card_id inexistente
    Then se lanza un CardNotFoundError

  # ─── DemoteToPreWorkflow — Happy path ────────────────────────────

  Scenario: Demote desde estado de workflow a BACKLOG por defecto
    Given una Card en workflow_state_id = "TO DO"
    When se ejecuta DemoteToPreWorkflow sin especificar stage
    Then la Card tiene pre_workflow_stage = BACKLOG
    And workflow_state_id es None
    And el card_index se actualiza: nuevo en BACKLOG, eliminado de TO DO

  Scenario: Demote especificando stage = INBOX
    Given una Card en workflow_state_id = "WIP"
    When se ejecuta DemoteToPreWorkflow con stage = INBOX
    Then la Card tiene pre_workflow_stage = INBOX

  Scenario: Demote desde estado End (reabrir Card archivada)
    Given una Card en workflow_state_id = "DONE" (End State)
    When se ejecuta DemoteToPreWorkflow con stage = BACKLOG
    Then la Card tiene pre_workflow_stage = BACKLOG

  # ─── DemoteToPreWorkflow — Business rule violations ──────────────

  Scenario: Demote de Card que ya está en pre-workflow es rechazado
    Given una Card en pre_workflow_stage = BACKLOG
    When se ejecuta DemoteToPreWorkflow
    Then se lanza un InvalidTransitionError indicando que la Card no está en el workflow

  # ─── Edge cases ──────────────────────────────────────────────────

  Scenario: Promote seguido de Demote deja la Card en BACKLOG
    Given una Card en pre_workflow_stage = BACKLOG
    When se ejecuta PromoteToWorkflow con target = "TO DO"
    And se ejecuta DemoteToPreWorkflow
    Then la Card está en pre_workflow_stage = BACKLOG

  Scenario: Promote al End State directamente es válido (caso urgente completado)
    Given una Card en pre_workflow_stage = BACKLOG
    When se ejecuta PromoteToWorkflow con target_state_id = "DONE" (End State)
    Then la Card tiene workflow_state_id = "DONE"
