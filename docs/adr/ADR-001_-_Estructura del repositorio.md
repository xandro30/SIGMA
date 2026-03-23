# ADR-001: Estructura del repositorio — mono-repo con dominio compartido

**Estado:** Aceptado
**Fecha:** 2026-03-21

## Contexto

SIGMA es una aplicación personal de productividad que requiere
tres componentes con ciclos de despliegue independientes pero
con dominio de negocio compartido:
- Un servidor MCP para interactuar con Claude
- Una API REST para la PWA y otros clientes
- Una PWA como interfaz de usuario

## Decisión

Mono-repo con dominio compartido mediante uv workspaces:
```
sigma/
├── packages/
│   ├── sigma-core/     ← dominio + puertos (Python)
│   ├── sigma-mcp/      ← adaptador MCP (Python)
│   ├── sigma-rest/     ← adaptador REST (Python)
│   └── sigma-web/      ← PWA (React)
└── docs/adr/
```

## Razonamiento

`sigma-core` contiene el dominio puro — entidades, casos de uso
y puertos. `sigma-mcp` y `sigma-rest` lo importan como
dependencia local. El dominio se escribe una sola vez.

uv workspaces soporta esta estructura nativamente — cada package
tiene su `pyproject.toml` pero comparten un único `uv.lock` raíz,
garantizando consistencia de dependencias entre packages Python.

## Alternativas consideradas

- **Repos separados**: mayor aislamiento pero duplicación del
  dominio o dependencia de un paquete publicado en PyPI.
  Descartado — complejidad innecesaria para un único desarrollador.
- **Un único package Python**: mezcla adaptadores con dominio
  en el mismo paquete. Descartado — viola la separación de
  capas de la arquitectura hexagonal.

## Consecuencias

- El dominio se define una vez en `sigma-core` y es consumido
  por todos los adaptadores Python
- Cambios en el dominio son visibles inmediatamente en todos
  los packages sin publicar a PyPI
- `sigma-web` es independiente — tiene su propio `package.json`
  y no participa en el workspace de uv
- Cada package se despliega de forma independiente en Cloud Run
  o Firebase Hosting según corresponda