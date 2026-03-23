Feature: Value Objects — validación e invariantes

  Los Value Objects son inmutables e identificados por valor.
  Validan sus invariantes en construcción (Fail Fast).
  Un VO inválido nunca puede ser creado.

  # ─── CardTitle ──────────────────────────────────────────────────

  Scenario: CardTitle válido con texto normal
    Given el texto "Implementar login con Google"
    When se crea un CardTitle con ese texto
    Then el CardTitle se crea correctamente
    And su valor es "Implementar login con Google"

  Scenario: CardTitle con espacios al inicio y al final se normaliza
    Given el texto "  Tarea con espacios  "
    When se crea un CardTitle con ese texto
    Then el CardTitle se crea correctamente
    And su valor es "Tarea con espacios"

  Scenario: CardTitle vacío es rechazado
    Given el texto ""
    When se intenta crear un CardTitle con ese texto
    Then se lanza un ValueError

  Scenario: CardTitle con solo espacios es rechazado
    Given el texto "   "
    When se intenta crear un CardTitle con ese texto
    Then se lanza un ValueError

  # Boundary: límite de 255 caracteres
  Scenario: CardTitle de exactamente 255 caracteres es válido
    Given un texto de exactamente 255 caracteres
    When se crea un CardTitle con ese texto
    Then el CardTitle se crea correctamente

  Scenario: CardTitle de 256 caracteres es rechazado
    Given un texto de exactamente 256 caracteres
    When se intenta crear un CardTitle con ese texto
    Then se lanza un ValueError

  Scenario: CardTitle de 1 carácter es válido
    Given el texto "X"
    When se crea un CardTitle con ese texto
    Then el CardTitle se crea correctamente

  # ─── Url ────────────────────────────────────────────────────────

  Scenario: URL https válida es aceptada
    Given la URL "https://firebase.google.com/docs"
    When se crea un Url con ese valor
    Then el Url se crea correctamente

  Scenario: URL http válida es aceptada
    Given la URL "http://localhost:8000/api"
    When se crea un Url con ese valor
    Then el Url se crea correctamente

  Scenario: URL sin esquema es rechazada
    Given la URL "firebase.google.com/docs"
    When se intenta crear un Url con ese valor
    Then se lanza un ValueError

  Scenario: URL con esquema ftp es rechazada
    Given la URL "ftp://files.example.com"
    When se intenta crear un Url con ese valor
    Then se lanza un ValueError

  Scenario: Cadena vacía es rechazada como URL
    Given la URL ""
    When se intenta crear un Url con ese valor
    Then se lanza un ValueError

  Scenario: Dos Url con el mismo valor son iguales
    Given la URL "https://example.com"
    When se crean dos instancias de Url con ese valor
    Then ambas instancias son iguales

  # ─── ChecklistItem ───────────────────────────────────────────────

  Scenario: ChecklistItem nuevo está sin completar por defecto
    Given el texto "Revisar documentación"
    When se crea un ChecklistItem con ese texto
    Then el item tiene done = False

  Scenario: complete() devuelve una nueva instancia con done = True
    Given un ChecklistItem con texto "Revisar documentación" y done = False
    When se llama a complete()
    Then se retorna un nuevo ChecklistItem con done = True
    And el ChecklistItem original no ha cambiado

  Scenario: reopen() devuelve una nueva instancia con done = False
    Given un ChecklistItem con texto "Revisar documentación" y done = True
    When se llama a reopen()
    Then se retorna un nuevo ChecklistItem con done = False

  Scenario: ChecklistItem con texto vacío es rechazado
    Given el texto ""
    When se intenta crear un ChecklistItem con ese texto
    Then se lanza un ValueError

  # Boundary: límite de 500 caracteres
  Scenario: ChecklistItem de exactamente 500 caracteres es válido
    Given un texto de exactamente 500 caracteres
    When se crea un ChecklistItem con ese texto
    Then el ChecklistItem se crea correctamente

  Scenario: ChecklistItem de 501 caracteres es rechazado
    Given un texto de exactamente 501 caracteres
    When se intenta crear un ChecklistItem con ese texto
    Then se lanza un ValueError

  # ─── IDs (CardId, SpaceId, etc.) ─────────────────────────────────

  Scenario: CardId generado es un UUID v4 válido
    When se genera un CardId con generate()
    Then el valor es un UUID v4 válido

  Scenario: CardId con UUID v4 válido es aceptado
    Given el string "550e8400-e29b-41d4-a716-446655440000"
    When se crea un CardId con ese valor
    Then el CardId se crea correctamente

  Scenario: CardId con string arbitrario es rechazado
    Given el string "no-es-un-uuid"
    When se intenta crear un CardId con ese valor
    Then se lanza un ValueError

  Scenario: Dos CardId con el mismo UUID son iguales
    Given el UUID "550e8400-e29b-41d4-a716-446655440000"
    When se crean dos instancias de CardId con ese UUID
    Then ambas instancias son iguales

  Scenario: Dos CardId con distinto UUID son distintos
    Given dos UUIDs diferentes
    When se crean dos instancias de CardId con esos UUIDs
    Then las instancias son distintas
