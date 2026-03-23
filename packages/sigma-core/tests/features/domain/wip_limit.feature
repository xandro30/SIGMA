Feature: WIP Limit — reglas de límite de Cards por estado

  WipLimitRule define un máximo de Cards simultáneas en un WorkflowState.
  El límite puede aplicar a todas las Cards o solo a las que pasen un CardFilter.
  La validación es responsabilidad del caso de uso, no del dominio.

  # ─── WipLimitRule — invariantes ──────────────────────────────────

  Scenario: WipLimitRule con max_cards = 1 es válida
    When se crea una WipLimitRule con max_cards = 1
    Then la regla se crea correctamente

  Scenario: WipLimitRule con max_cards = 0 es rechazada
    When se intenta crear una WipLimitRule con max_cards = 0
    Then se lanza un ValueError

  Scenario: WipLimitRule con max_cards negativo es rechazada
    When se intenta crear una WipLimitRule con max_cards = -1
    Then se lanza un ValueError

  Scenario: WipLimitRule sin filtro aplica a todas las Cards
    Given una WipLimitRule con max_cards = 3 y filter = None
    Then la regla aplica a todas las Cards del estado

  Scenario: WipLimitRule con filtro aplica solo a Cards que lo pasen
    Given una WipLimitRule con max_cards = 2 y filter con priority = [critical]
    Then la regla solo aplica a Cards con priority = critical

  # ─── Evaluación del límite (simulada en dominio) ──────────────────

  Scenario: Estado con límite no superado permite el movimiento
    Given un WorkflowState con WipLimitRule max_cards = 3 y filter = None
    And hay 2 Cards actualmente en ese estado
    When el caso de uso evalúa si se puede añadir una Card más
    Then el movimiento es permitido

  Scenario: Estado con límite exactamente alcanzado bloquea el movimiento
    Given un WorkflowState con WipLimitRule max_cards = 3 y filter = None
    And hay 3 Cards actualmente en ese estado
    When el caso de uso evalúa si se puede añadir una Card más
    Then el movimiento es bloqueado por WipLimitExceededError

  Scenario: Límite con filtro solo cuenta Cards que pasan el filtro
    Given un WorkflowState con WipLimitRule max_cards = 2 y filter con priority = [critical]
    And hay 3 Cards en el estado pero solo 1 es de priority = critical
    When el caso de uso evalúa mover una Card con priority = critical
    Then el movimiento es permitido (1 < 2)

  Scenario: Límite con filtro bloqueado por Cards que pasan el filtro
    Given un WorkflowState con WipLimitRule max_cards = 2 y filter con priority = [critical]
    And hay 2 Cards de priority = critical en el estado
    When el caso de uso evalúa mover una Card con priority = critical
    Then el movimiento es bloqueado por WipLimitExceededError

  Scenario: Límite con filtro no afecta a Cards que no pasan el filtro
    Given un WorkflowState con WipLimitRule max_cards = 2 y filter con priority = [critical]
    And hay 2 Cards de priority = critical en el estado
    When el caso de uso evalúa mover una Card con priority = low
    Then el movimiento es permitido (la Card no es contada por el filtro)

  # ─── Múltiples reglas por estado ──────────────────────────────────

  Scenario: Estado con múltiples WipLimitRules bloquea si cualquiera de ellas falla
    Given un WorkflowState con dos reglas:
      | max_cards | filter              |
      | 5         | None                |
      | 2         | priority = critical |
    And hay 4 Cards en total y 2 de ellas con priority = critical
    When el caso de uso evalúa mover una Card con priority = critical
    Then el movimiento es bloqueado (la segunda regla está al límite)

  Scenario: Estado con múltiples WipLimitRules permite si todas se cumplen
    Given un WorkflowState con dos reglas:
      | max_cards | filter              |
      | 5         | None                |
      | 2         | priority = critical |
    And hay 3 Cards en total y 1 de ellas con priority = critical
    When el caso de uso evalúa mover una Card con priority = critical
    Then el movimiento es permitido (ambas reglas tienen margen)

  # ─── Edge cases ───────────────────────────────────────────────────

  Scenario: Estado sin WipLimitRules siempre permite el movimiento
    Given un WorkflowState sin ninguna WipLimitRule
    And hay 100 Cards en ese estado
    When el caso de uso evalúa si se puede añadir una Card más
    Then el movimiento es permitido

  Scenario: Evaluación con 0 Cards en el estado siempre permite el movimiento
    Given un WorkflowState con WipLimitRule max_cards = 1
    And hay 0 Cards en ese estado
    When el caso de uso evalúa si se puede añadir una Card más
    Then el movimiento es permitido
