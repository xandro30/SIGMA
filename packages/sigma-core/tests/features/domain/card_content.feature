Feature: Card Content — labels, topics, urls, checklist y related cards

  Operaciones sobre el contenido de una Card.
  Las listas son idempotentes en add y no permiten duplicados.

  # ─── Labels ──────────────────────────────────────────────────────

  Scenario: Añadir una label a una Card sin labels
    Given una Card sin labels
    When se llama a add_label("#SecOps")
    Then la Card tiene la label "#SecOps"
    And updated_at ha sido actualizado

  Scenario: Añadir la misma label dos veces es idempotente
    Given una Card con la label "#SecOps"
    When se llama a add_label("#SecOps") de nuevo
    Then la Card tiene exactamente una label "#SecOps"

  Scenario: Eliminar una label existente
    Given una Card con las labels "#SecOps" y "#España"
    When se llama a remove_label("#SecOps")
    Then la Card tiene solo la label "#España"

  Scenario: Eliminar una label que no existe no lanza error
    Given una Card sin labels
    When se llama a remove_label("#Inexistente")
    Then no se lanza ningún error

  Scenario: Label vacía es rechazada
    Given una Card sin labels
    When se intenta añadir la label ""
    Then se lanza un ValueError

  Scenario: Label con solo espacios es rechazada
    Given una Card sin labels
    When se intenta añadir la label "   "
    Then se lanza un ValueError

  # ─── Topics ──────────────────────────────────────────────────────

  Scenario: Añadir un topic nuevo
    Given una Card sin topics
    When se llama a add_topic("IAM")
    Then la Card tiene el topic "IAM"

  Scenario: Añadir el mismo topic dos veces es idempotente
    Given una Card con el topic "IAM"
    When se llama a add_topic("IAM") de nuevo
    Then la Card tiene exactamente un topic "IAM"

  Scenario: Eliminar un topic existente
    Given una Card con los topics "IAM" y "GCP"
    When se llama a remove_topic("IAM")
    Then la Card tiene solo el topic "GCP"

  # ─── URLs ────────────────────────────────────────────────────────

  Scenario: Añadir una URL válida
    Given una Card sin URLs
    When se llama a add_url con "https://docs.google.com"
    Then la Card tiene la URL "https://docs.google.com"

  Scenario: Añadir la misma URL dos veces es idempotente
    Given una Card con la URL "https://docs.google.com"
    When se llama a add_url con "https://docs.google.com" de nuevo
    Then la Card tiene exactamente una URL "https://docs.google.com"

  Scenario: Eliminar una URL existente
    Given una Card con dos URLs
    When se llama a remove_url con la primera URL
    Then la Card tiene solo la segunda URL

  # ─── Checklist ───────────────────────────────────────────────────

  Scenario: Añadir un ítem al checklist
    Given una Card con checklist vacío
    When se llama a add_checklist_item con texto "Revisar docs"
    Then el checklist tiene un ítem "Revisar docs" con done = False

  Scenario: Añadir un ítem duplicado al checklist es rechazado
    Given una Card con el ítem "Revisar docs" en el checklist
    When se intenta añadir otro ítem con el mismo texto "Revisar docs"
    Then se lanza un DuplicateChecklistItemError

  Scenario: toggle_checklist_item marca como completado un ítem pendiente
    Given una Card con el ítem "Revisar docs" con done = False
    When se llama a toggle_checklist_item("Revisar docs")
    Then el ítem "Revisar docs" tiene done = True

  Scenario: toggle_checklist_item reabre un ítem completado
    Given una Card con el ítem "Revisar docs" con done = True
    When se llama a toggle_checklist_item("Revisar docs")
    Then el ítem "Revisar docs" tiene done = False

  Scenario: checklist_progress reporta completados sobre total
    Given una Card con 3 ítems donde 2 están completados
    When se llama a checklist_progress()
    Then retorna (2, 3)

  Scenario: checklist_progress con checklist vacío retorna (0, 0)
    Given una Card con checklist vacío
    When se llama a checklist_progress()
    Then retorna (0, 0)

  Scenario: Eliminar un ítem del checklist
    Given una Card con los ítems "A" y "B" en el checklist
    When se llama a remove_checklist_item("A")
    Then el checklist tiene solo el ítem "B"

  Scenario: toggle sobre ítem inexistente no muta el checklist
    Given una Card con el ítem "A" en el checklist
    When se llama a toggle_checklist_item("Inexistente")
    Then el checklist no ha cambiado

  # ─── Related Cards ───────────────────────────────────────────────

  Scenario: Añadir una Card relacionada
    Given una Card A sin cards relacionadas
    And una Card B con ID diferente
    When se llama a add_related_card con el ID de la Card B
    Then related_cards contiene el ID de la Card B

  Scenario: Añadir la misma Card relacionada dos veces es idempotente
    Given una Card A con la Card B en related_cards
    When se llama a add_related_card con el ID de la Card B de nuevo
    Then related_cards contiene exactamente una vez el ID de la Card B

  Scenario: Una Card no puede relacionarse consigo misma
    Given una Card A
    When se intenta añadir el propio ID de la Card A en related_cards
    Then se lanza un ValueError indicando auto-referencia

  Scenario: Crear una Card con su propio ID en related_cards es rechazado
    When se intenta crear una Card con su propio ID en related_cards
    Then se lanza un ValueError indicando auto-referencia

  Scenario: Eliminar una Card relacionada
    Given una Card A con las Cards B y C en related_cards
    When se llama a remove_related_card con el ID de la Card B
    Then related_cards contiene solo el ID de la Card C
