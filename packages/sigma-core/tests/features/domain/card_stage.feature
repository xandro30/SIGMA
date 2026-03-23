Feature: Card Stage — discriminated union y transiciones de etapa

  Una Card siempre está en exactamente uno de dos estados mutuamente
  excluyentes: pre_workflow_stage O workflow_state_id.
  Nunca ambos activos, nunca ninguno activo.

  # ─── Invariante del discriminated union ─────────────────────────

  Scenario: Card creada con pre_workflow_stage tiene workflow_state_id nulo
    Given una Card con pre_workflow_stage = INBOX
    Then workflow_state_id es None
    And is_in_pre_workflow() retorna True
    And is_in_workflow() retorna False

  Scenario: Card creada con workflow_state_id tiene pre_workflow_stage nulo
    Given una Card con workflow_state_id = "uuid-state"
    Then pre_workflow_stage es None
    And is_in_workflow() retorna True
    And is_in_pre_workflow() retorna False

  Scenario: Card con ambos campos activos es rechazada
    When se intenta crear una Card con pre_workflow_stage = INBOX y workflow_state_id = "uuid-state"
    Then se lanza un ValueError indicando invariante de stage violado

  Scenario: Card sin ningún campo activo es rechazada
    When se intenta crear una Card con pre_workflow_stage = None y workflow_state_id = None
    Then se lanza un ValueError indicando invariante de stage violado

  # ─── Transiciones desde pre-workflow ─────────────────────────────

  Scenario: move_to_pre_workflow cambia de INBOX a REFINEMENT
    Given una Card en pre_workflow_stage = INBOX
    When se llama a move_to_pre_workflow(REFINEMENT)
    Then pre_workflow_stage es REFINEMENT
    And workflow_state_id es None
    And updated_at ha sido actualizado

  Scenario: move_to_pre_workflow desde workflow activa el pre-workflow
    Given una Card con workflow_state_id = "uuid-state"
    When se llama a move_to_pre_workflow(BACKLOG)
    Then pre_workflow_stage es BACKLOG
    And workflow_state_id es None

  Scenario: move_to_workflow_state activa el workflow
    Given una Card en pre_workflow_stage = BACKLOG
    When se llama a move_to_workflow_state("uuid-state")
    Then workflow_state_id es "uuid-state"
    And pre_workflow_stage es None
    And updated_at ha sido actualizado

  Scenario: move_to_workflow_state desde otro estado de workflow cambia el estado
    Given una Card con workflow_state_id = "uuid-state-1"
    When se llama a move_to_workflow_state("uuid-state-2")
    Then workflow_state_id es "uuid-state-2"
    And pre_workflow_stage es None

  # ─── Idempotencia ────────────────────────────────────────────────

  Scenario: Mover a la misma etapa pre-workflow no rompe el invariante
    Given una Card en pre_workflow_stage = BACKLOG
    When se llama a move_to_pre_workflow(BACKLOG)
    Then pre_workflow_stage es BACKLOG
    And workflow_state_id es None

  # ─── updated_at ──────────────────────────────────────────────────

  Scenario: updated_at se actualiza en cada movimiento
    Given una Card con un updated_at inicial
    When se llama a move_to_pre_workflow(REFINEMENT)
    Then updated_at es posterior al valor inicial
