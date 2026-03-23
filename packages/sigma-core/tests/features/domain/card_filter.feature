Feature: CardFilter — motor de predicados

  CardFilter evalúa predicados sobre las propiedades de una Card.
  Los filtros activos se combinan con AND.
  Un CardFilter vacío pasa todas las Cards.

  # ─── Filtro vacío ────────────────────────────────────────────────

  Scenario: CardFilter vacío acepta cualquier Card
    Given un CardFilter sin ningún filtro activo
    And una Card con cualquier valor
    When se llama a matches(card)
    Then retorna True

  # ─── String predicates ───────────────────────────────────────────

  Scenario: StringEquals filtra por coincidencia exacta en título
    Given un CardFilter con title = StringEquals("Revisar logs")
    When se evalúa contra una Card con título "Revisar logs"
    Then matches retorna True

  Scenario: StringEquals rechaza título diferente
    Given un CardFilter con title = StringEquals("Revisar logs")
    When se evalúa contra una Card con título "Otro título"
    Then matches retorna False

  Scenario: StringContains filtra por contenido parcial en título
    Given un CardFilter con title = StringContains("logs")
    When se evalúa contra una Card con título "Revisar logs de Chronicle"
    Then matches retorna True

  Scenario: StringNotContains rechaza título que contiene el valor
    Given un CardFilter con title = StringNotContains("urgente")
    When se evalúa contra una Card con título "Tarea urgente"
    Then matches retorna False

  Scenario: StringNotContains acepta título que no contiene el valor
    Given un CardFilter con title = StringNotContains("urgente")
    When se evalúa contra una Card con título "Tarea normal"
    Then matches retorna True

  # ─── List predicates ─────────────────────────────────────────────

  Scenario: ListHasAny acepta Card con al menos uno de los valores
    Given un CardFilter con labels = ListHasAny({"#SecOps", "#España"})
    When se evalúa contra una Card con labels ["#SecOps", "#BBVA"]
    Then matches retorna True

  Scenario: ListHasAny rechaza Card sin ninguno de los valores
    Given un CardFilter con labels = ListHasAny({"#SecOps", "#España"})
    When se evalúa contra una Card con labels ["#Personal"]
    Then matches retorna False

  Scenario: ListHasAll acepta Card con todos los valores requeridos
    Given un CardFilter con topics = ListHasAll({"IAM", "GCP"})
    When se evalúa contra una Card con topics ["IAM", "GCP", "Chronicle"]
    Then matches retorna True

  Scenario: ListHasAll rechaza Card a la que le falta algún valor requerido
    Given un CardFilter con topics = ListHasAll({"IAM", "GCP"})
    When se evalúa contra una Card con topics ["IAM"]
    Then matches retorna False

  Scenario: ListHasNone acepta Card sin ninguno de los valores excluidos
    Given un CardFilter con topics = ListHasNone({"deprecated", "blocked"})
    When se evalúa contra una Card con topics ["IAM", "GCP"]
    Then matches retorna True

  Scenario: ListHasNone rechaza Card con alguno de los valores excluidos
    Given un CardFilter con topics = ListHasNone({"deprecated"})
    When se evalúa contra una Card con topics ["IAM", "deprecated"]
    Then matches retorna False

  Scenario: ListHasAny contra lista vacía en la Card retorna False
    Given un CardFilter con labels = ListHasAny({"#SecOps"})
    When se evalúa contra una Card sin labels
    Then matches retorna False

  # ─── Date predicates ─────────────────────────────────────────────

  Scenario: DateBefore acepta Card con due_date anterior a la fecha límite
    Given un CardFilter con due_date = DateBefore(2026-04-01)
    When se evalúa contra una Card con due_date = 2026-03-25
    Then matches retorna True

  Scenario: DateBefore rechaza Card con due_date igual o posterior
    Given un CardFilter con due_date = DateBefore(2026-04-01)
    When se evalúa contra una Card con due_date = 2026-04-01
    Then matches retorna False

  Scenario: DateAfter acepta Card con due_date posterior a la fecha
    Given un CardFilter con due_date = DateAfter(2026-03-01)
    When se evalúa contra una Card con due_date = 2026-03-25
    Then matches retorna True

  Scenario: Filtro de fecha contra Card sin due_date no aplica el filtro
    Given un CardFilter con due_date = DateBefore(2026-04-01)
    When se evalúa contra una Card sin due_date
    Then matches retorna True

  # ─── Combinación de filtros (AND) ────────────────────────────────

  Scenario: Múltiples filtros activos se combinan con AND
    Given un CardFilter con priority = [high, critical] y topics = ListHasAny({"IAM"})
    When se evalúa contra una Card con priority = high y topics = ["IAM", "GCP"]
    Then matches retorna True

  Scenario: Un filtro fallido rechaza la Card aunque el resto pasen
    Given un CardFilter con priority = [high] y topics = ListHasAny({"IAM"})
    When se evalúa contra una Card con priority = low y topics = ["IAM"]
    Then matches retorna False

  # ─── Filtro por stage ─────────────────────────────────────────────

  Scenario: Filtro por pre_workflow_stage acepta Card en ese stage
    Given un CardFilter con pre_workflow_stage = [INBOX]
    When se evalúa contra una Card en pre_workflow_stage = INBOX
    Then matches retorna True

  Scenario: Filtro por workflow_state_id acepta Card en ese estado
    Given un CardFilter con workflow_state_id = ["uuid-wip"]
    When se evalúa contra una Card con workflow_state_id = "uuid-wip"
    Then matches retorna True

  Scenario: Filtro por workflow_state_id rechaza Card en stage distinto
    Given un CardFilter con workflow_state_id = ["uuid-wip"]
    When se evalúa contra una Card en pre_workflow_stage = INBOX
    Then matches retorna False
