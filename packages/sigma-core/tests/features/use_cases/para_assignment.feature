Feature: PARA Assignment — Area, Project y Epic

  Las Cards pueden clasificarse opcionalmente en Areas, Projects y Epics.
  Un Card puede existir sin ninguna de estas clasificaciones (huérfano).
  Un Project siempre pertenece a un Area.
  Al asignar un Project a una Card, el Area se infiere automáticamente.

  Background:
    Given un Area "BBVA" con ID "uuid-area"
    And un Project "N3 SecOps" con ID "uuid-project" y area_id = "uuid-area"
    And un Epic "Auth Module" con ID "uuid-epic"
    And una Card huérfana en INBOX

  # ─── AssignArea ───────────────────────────────────────────────────

  Scenario: Asignar un Area a una Card huérfana
    When se ejecuta AssignArea con area_id = "uuid-area"
    Then la Card tiene area_id = "uuid-area"
    And project_id sigue siendo None

  Scenario: Cambiar el Area de una Card
    Given una Card con area_id = "uuid-area-1"
    When se ejecuta AssignArea con area_id = "uuid-area-2"
    Then la Card tiene area_id = "uuid-area-2"

  Scenario: Desasignar Area poniendo area_id = None
    Given una Card con area_id = "uuid-area"
    When se ejecuta AssignArea con area_id = None
    Then la Card tiene area_id = None

  Scenario: Asignar Area inexistente es rechazado
    When se ejecuta AssignArea con area_id = "uuid-inexistente"
    Then se lanza un AreaNotFoundError

  # ─── AssignProject ────────────────────────────────────────────────

  Scenario: Asignar un Project infiere el Area automáticamente
    Given una Card sin area_id ni project_id
    When se ejecuta AssignProject con project_id = "uuid-project"
    Then la Card tiene project_id = "uuid-project"
    And la Card tiene area_id = "uuid-area" (inferido del Project)

  Scenario: Asignar un Project sobreescribe el Area existente si es diferente
    Given una Card con area_id = "uuid-area-otro"
    When se ejecuta AssignProject con project_id = "uuid-project"
    Then la Card tiene area_id = "uuid-area" (la del Project)

  Scenario: Desasignar Project poniendo project_id = None no elimina el Area
    Given una Card con project_id = "uuid-project" y area_id = "uuid-area"
    When se ejecuta AssignProject con project_id = None
    Then la Card tiene project_id = None
    And la Card tiene area_id = "uuid-area"

  Scenario: Asignar Project inexistente es rechazado
    When se ejecuta AssignProject con project_id = "uuid-inexistente"
    Then se lanza un ProjectNotFoundError

  # ─── AssignEpic ───────────────────────────────────────────────────

  Scenario: Asignar un Epic a una Card
    When se ejecuta AssignEpic con epic_id = "uuid-epic"
    Then la Card tiene epic_id = "uuid-epic"

  Scenario: Desasignar Epic poniendo epic_id = None
    Given una Card con epic_id = "uuid-epic"
    When se ejecuta AssignEpic con epic_id = None
    Then la Card tiene epic_id = None

  Scenario: Asignar Epic inexistente es rechazado
    When se ejecuta AssignEpic con epic_id = "uuid-inexistente"
    Then se lanza un EpicNotFoundError

  Scenario: Asignar Epic de otro Space es rechazado
    Given un Epic "Foreign Epic" que pertenece al Space "Personal", no a "Work"
    When se ejecuta AssignEpic con ese epic_id sobre una Card del Space "Work"
    Then se lanza un InvalidEpicSpaceError

  # ─── DeleteArea — efecto sobre Cards ─────────────────────────────

  Scenario: Eliminar un Area deja las Cards con area_id = None
    Given una Card con area_id = "uuid-area"
    When se ejecuta DeleteArea con area_id = "uuid-area"
    Then la Card tiene area_id = None

  Scenario: Eliminar un Area deja los Projects con area_id huérfanos
    Given el Project "N3 SecOps" con area_id = "uuid-area"
    When se ejecuta DeleteArea con area_id = "uuid-area"
    Then el Project tiene area_id = None

  # ─── DeleteProject — efecto sobre Cards ──────────────────────────

  Scenario: Eliminar un Project deja las Cards con project_id = None
    Given una Card con project_id = "uuid-project"
    When se ejecuta DeleteProject con project_id = "uuid-project"
    Then la Card tiene project_id = None
    And la Card conserva su area_id

  # ─── DeleteEpic — efecto sobre Cards ────────────────────────────

  Scenario: Eliminar un Epic deja las Cards con epic_id = None
    Given una Card con epic_id = "uuid-epic"
    When se ejecuta DeleteEpic con epic_id = "uuid-epic"
    Then la Card tiene epic_id = None

  # ─── Edge cases ──────────────────────────────────────────────────

  Scenario: Card puede existir sin Area, Project ni Epic (huérfano válido)
    Given una Card recién creada sin clasificación
    Then area_id es None
    And project_id es None
    And epic_id es None
    And la Card es válida

  Scenario: Card con solo Area (sin Project) es válida
    Given una Card con area_id = "uuid-area" y project_id = None
    Then la Card es válida

  Scenario: Project sin Area directa es inválido
    When se intenta crear un Project sin area_id
    Then se lanza un ValueError
