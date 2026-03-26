# ADR-013: Estrategia de testing — TDD con pytest

**Estado:** Aceptado
**Fecha:** 2026-03-24
**Reemplaza:** versión anterior con behave + Gherkin

## Contexto

`sigma-core` contiene el dominio puro del sistema — aggregates, value objects
y casos de uso. Es el núcleo más crítico y el que más se beneficia de una
cobertura deliberada. Se necesita una estrategia de testing que:

- Sea intuitiva y de bajo fricción para un único desarrollador
- Evite múltiples fuentes de verdad
- Identifique los casos conflictivos sin generar tests redundantes
- Permita un ciclo TDD rápido

## Decisión

**pytest** como único framework de testing para dominio e integración.
Los tests siguen la semántica Given/When/Then como comentarios inline
— no como infraestructura ejecutable separada.

```python
def test_card_title_valido_se_crea_correctamente():
    # Given
    text = "Implementar login con Google"

    # When
    result = CardTitle(text)

    # Then
    assert isinstance(result, CardTitle)
    assert result.value == text
```

Los tests se organizan en tres categorías deliberadas:

| Categoría | Qué cubre |
|---|---|
| **Happy path** | Flujo nominal completo — define el comportamiento esperado |
| **Edge cases** | Colección vacía, un solo elemento, idempotencia, auto-referencia |
| **Boundary Value Analysis** | Rangos con límite: valor en el límite, uno dentro, uno fuera |

Lo que **no** se testea: combinaciones arbitrarias de campos válidos,
comportamientos ya cubiertos por otro test, internals de implementación.

## Estructura

```
sigma-core/
  tests/
    unit/
      domain/
        test_value_objects.py
        test_card.py
        test_space.py
        test_card_filter.py
        test_wip_limit.py
      use_cases/
        test_create_card.py
        test_move_card.py
        test_promote_demote.py
        test_para_assignment.py
    fakes/
      fake_card_repository.py
      fake_space_repository.py
      fake_area_repository.py
      fake_project_repository.py
      fake_epic_repository.py
    integration/           ← adaptadores contra emulador Firestore
```

## Razonamiento

La aproximación BDD con behave + feature files fue evaluada y descartada
por las siguientes razones concretas:

- **Dos fuentes de verdad**: el feature file y el step definition deben
  mantenerse sincronizados manualmente. Cuando el dominio cambia, hay que
  actualizar ambos — es complejidad accidental sin beneficio real para un
  único desarrollador.
- **Fricción alta**: los step definitions son infraestructura de testing
  pura que no aporta lógica de negocio. Escribir un step por cada línea
  Gherkin ralentiza el ciclo TDD sin añadir cobertura.
- **Poca intuitividad**: la separación entre feature file y step definitions
  dificulta la lectura — para entender un test hay que navegar entre dos
  ficheros y entender el mecanismo de matching por texto.

pytest con comentarios Given/When/Then inline consigue el mismo valor
semántico sin la infraestructura adicional. El test es autocontenido,
directamente ejecutable, y la fuente de verdad es única.

## Alternativas consideradas

- **behave + Gherkin**: evaluado e implementado parcialmente. Descartado
  por las razones expuestas — dos fuentes de verdad, alta fricción,
  baja intuitividad para un único desarrollador.
- **unittest**: más verboso que pytest, sin ventajas adicionales para
  este caso. Descartado.

## Consecuencias

- Una única fuente de verdad — el código de producción y sus tests
- Ciclo TDD directo: escribe el test, vélo fallar, implementa, vélo pasar
- Los tests de dominio son unitarios puros — sin mocks, sin base de datos,
  solo objetos de dominio en memoria
- Los fakes en `tests/fakes/` implementan los Protocols de repositorio
  con diccionarios en memoria para los tests de casos de uso
- La integración con Firestore se cubre en `tests/integration/`
  con el emulador local de Firestore
- Ejecución: `uv run pytest` para todo, `uv run pytest tests/unit/`
  para solo dominio, `uv run pytest tests/integration/` para adaptadores