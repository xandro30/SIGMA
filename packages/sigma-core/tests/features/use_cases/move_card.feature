Feature: MoveCard — movimiento entre estados del workflow

  MoveWithinWorkflow mueve una Card entre estados del workflow configurable.
  Valida: que la transición esté permitida, que no se supere el WIP limit.
  La validación ocurre antes de mutar la Card.

  Background:
    Given un Space "Work" con el siguiente workflow:
      | nombre | is_start | is_end | wip_limit | allowed_transitions |
      | TO DO  | true     | false  | —         | WIP                 |
      | WIP    | false    | false  | 3         | DONE                |
      | DONE   | false    | true   | —         | —                   |
    And una Card en workflow_state_id = "TO DO"

  # ─── Happy path ───────────────────────────────────────────────────

  Scenario: Mover Card de TO DO a WIP con espacio disponible
    Given hay 1 Card en el estado WIP
    When se ejecuta MoveWithinWorkflow con target_state_id = "WIP"
    Then la Card tiene workflow_state_id = "WIP"
    And updated_at ha sido actualizado
    And el card_index se actualiza: nuevo en WIP, eliminado de TO DO

  Scenario: Mover Card a estado End (DONE)
    Given una Card en el estado WIP
    When se ejecuta MoveWithinWorkflow con target_state_id = "DONE"
    Then la Card tiene workflow_state_id = "DONE"

  # ─── Business rule violations ────────────────────────────────────

  Scenario: Transición no permitida es rechazada
    Given una Card en el estado TO DO (allowed_transitions = [WIP])
    When se ejecuta MoveWithinWorkflow con target_state_id = "DONE"
    Then se lanza un InvalidTransitionError
    And la Card sigue en workflow_state_id = "TO DO"
    And no se escribe nada en el repositorio

  Scenario: WIP limit alcanzado bloquea el movimiento
    Given hay 3 Cards en el estado WIP (límite = 3)
    When se ejecuta MoveWithinWorkflow con target_state_id = "WIP"
    Then se lanza un WipLimitExceededError con state="WIP", limit=3, current=3
    And la Card sigue en workflow_state_id = "TO DO"
    And no se escribe nada en el repositorio

  Scenario: WIP limit con filtro bloquea solo si la Card lo supera
    Given un estado WIP con WipLimitRule max_cards=2 y filter priority=[critical]
    And hay 2 Cards de priority=critical en WIP
    And la Card a mover tiene priority=critical
    When se ejecuta MoveWithinWorkflow con target_state_id = "WIP"
    Then se lanza un WipLimitExceededError

  Scenario: WIP limit con filtro no bloquea si la Card no lo supera
    Given un estado WIP con WipLimitRule max_cards=2 y filter priority=[critical]
    And hay 2 Cards de priority=critical en WIP
    And la Card a mover tiene priority=low
    When se ejecuta MoveWithinWorkflow con target_state_id = "WIP"
    Then la Card se mueve correctamente

  # ─── Validation fails ────────────────────────────────────────────

  Scenario: Card inexistente es rechazada
    When se ejecuta MoveWithinWorkflow con card_id inexistente
    Then se lanza un CardNotFoundError

  Scenario: Estado destino inexistente en el Space es rechazado
    When se ejecuta MoveWithinWorkflow con target_state_id inexistente
    Then se lanza un StateNotFoundError

  Scenario: Mover Card que está en pre-workflow con MoveWithinWorkflow es rechazado
    Given una Card en pre_workflow_stage = BACKLOG (no en workflow)
    When se ejecuta MoveWithinWorkflow con cualquier target_state_id
    Then se lanza un InvalidTransitionError indicando que la Card no está en el workflow

  # ─── Edge cases ──────────────────────────────────────────────────

  Scenario: WIP limit justo por debajo del límite permite el movimiento
    Given hay 2 Cards en el estado WIP (límite = 3)
    When se ejecuta MoveWithinWorkflow con target_state_id = "WIP"
    Then la Card se mueve correctamente

  Scenario: Estado sin WipLimitRules acepta cualquier cantidad de Cards
    Given un estado sin WipLimitRule
    And hay 50 Cards en ese estado
    When se ejecuta MoveWithinWorkflow hacia ese estado
    Then la Card se mueve correctamente

  Scenario: Estado con allowed_transitions vacío acepta cualquier transición
    Given un Space donde el estado "FLEXIBLE" tiene allowed_transitions = []
    And una Card en el estado "FLEXIBLE"
    When se ejecuta MoveWithinWorkflow con target_state_id = cualquier estado del Space
    Then la Card se mueve correctamente
