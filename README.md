# SIGMA

Sistema personal de gestión de tareas con workflow configurable, integración con Claude vía MCP y acceso web mediante PWA.

---

## ¿Qué es SIGMA?

SIGMA reemplaza Trello + Planyway como sistema central de productividad personal. Combina un tablero Kanban con workflow configurable (estados, transiciones, WIP limits), clasificación PARA (Areas y Proyectos), y acceso desde Claude como agente de IA.

**Características principales:**

- **Tablero configurable** — define tus propios estados, transiciones y reglas WIP limit
- **Pre-workflow fijo** — Inbox → Refinement → Backlog como etapas universales de captura
- **Clasificación PARA** — Areas, Proyectos y Epics para organizar el trabajo por contexto
- **Acceso dual** — interfaz web PWA y agente Claude vía MCP desde la misma base de dominio
- **CardFilter** — motor de predicados para filtrar y visualizar cards en tablero y WIP limits
- **GCP free tier** — coste efectivo $0/mes para uso personal

---

## Estructura del repositorio

```
sigma/
├── README.md                        ← este fichero
├── ARCHITECTURE.md                  ← visión arquitectónica de referencia
├── pyproject.toml                   ← uv workspace raíz
├── uv.lock
│
├── packages/
│   ├── sigma-core/                  ← dominio puro + puertos (Python)
│   ├── sigma-mcp/                   ← adaptador MCP para Claude (Python)
│   ├── sigma-rest/                  ← adaptador REST + Firestore (Python)
│   └── sigma-web/                   ← PWA React (TypeScript)
│
└── docs/
    ├── adr/                         ← Architecture Decision Records
    │   ├── ADR-001_-_Estructura_del_repositorio.md
    │   ├── ADR-002_-_Stack_de_infraestructura_GCP.md
    │   ├── ADR-003_-_Base_de_datos_Firestore.md     ← Superseded
    │   ├── ADR-004_-_Gestion_de_secretos.md
    │   ├── ADR-005_-_Comunicacion_entre_componentes.md
    │   ├── ADR-006_-_Bounded_Context.md
    │   ├── ADR-007_-_Space_Aggregate_Root.md
    │   ├── ADR-008_-_Card_Aggregate_Root.md
    │   ├── ADR-009_-_PreWorkflowStage.md
    │   ├── ADR-010_-_WIP_Limit.md
    │   ├── ADR-011_-_Area_Project_PARA.md
    │   └── ADR-012_-_Column_Presentacion.md
    │
    └── design/
        ├── DOMAIN-DESIGN.md             ← modelo de dominio completo
        ├── FIRESTORE-DESIGN.md          ← colecciones, índices, fanout
        ├── UI-DESIGN.md                 ← wireframes y flujos de interfaz
        ├── COMMUNICATION-FLOWS.md       ← sequence diagrams de casos de uso
        ├── ARCHITECTURE-DIAGRAM.md      ← diagramas de arquitectura
        ├── API-REST-CATALOGUE.md        ← contratos REST completos
        └── MCP-TOOLS-CATALOGUE.md       ← tools MCP expuestas a Claude
```

---

## Stack técnico

| Capa | Tecnología |
|---|---|
| Dominio | Python 3.13 — puro, sin frameworks |
| API REST | FastAPI + pydantic-settings |
| Servidor MCP | FastMCP (`mcp[cli]`) |
| Base de datos | Firestore (GCP) |
| Autenticación | Firebase Auth (Google OAuth) |
| PWA | React + TypeScript |
| Hosting | Firebase Hosting |
| Compute | Cloud Run (containerizado) |
| Secretos | Secret Manager |
| Gestión de paquetes Python | uv workspaces |

---

## Arquitectura en una imagen

```mermaid
flowchart TD
    Dev(["👤 Usuario"])
    Claude(["🤖 Claude"])

    subgraph GCP ["Google Cloud Platform"]
        FH["Firebase Hosting\nsigma-web"]
        CR1["Cloud Run\nsigma-rest"]
        CR2["Cloud Run\nsigma-mcp"]
        FS[("Firestore")]
        FA["Firebase Auth"]
    end

    Dev -->|browser| FH
    FH -->|REST| CR1
    Claude -->|MCP| CR2
    CR1 --> FS
    CR2 --> FS
    CR1 --> FA
```

Para la arquitectura completa con todas las capas, dependencias e infraestructura → [`ARCHITECTURE.md`](./ARCHITECTURE.md)

---

## Quickstart

### Requisitos previos

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) instalado
- Node.js 20+ (para `sigma-web`)
- Proyecto GCP con Firestore, Firebase Auth y Secret Manager habilitados
- Firebase CLI instalado

### Instalación

```bash
# Clonar el repositorio
git clone <repo-url>
cd sigma

# Instalar todas las dependencias Python
uv sync

# Instalar dependencias de sigma-web
cd packages/sigma-web
npm install
```

### Configuración local

Crea un fichero `.env` en cada package Python a partir de su `.env.example`:

```bash
cp packages/sigma-rest/.env.example packages/sigma-rest/.env
cp packages/sigma-mcp/.env.example packages/sigma-mcp/.env
```

Variables mínimas necesarias:

```bash
# packages/sigma-rest/.env
FIRESTORE_PROJECT_ID=<tu-gcp-project-id>
FIRESTORE_DATABASE=(default)
FIREBASE_AUTH_CREDENTIALS=<path-to-service-account.json>

# packages/sigma-mcp/.env
FIRESTORE_PROJECT_ID=<tu-gcp-project-id>
FIRESTORE_DATABASE=(default)
```

### Ejecutar en local

```bash
# Dominio + API REST
cd packages/sigma-rest
uv run uvicorn sigma_rest.main:app --reload --port 8000

# Servidor MCP
cd packages/sigma-mcp
uv run mcp dev sigma_mcp/server.py

# PWA
cd packages/sigma-web
npm run dev
```

---

## Desarrollo

### Tests

```bash
# Tests de dominio (sigma-core)
cd packages/sigma-core
uv run pytest

# Tests de integración (sigma-rest)
cd packages/sigma-rest
uv run pytest
```

### Convenciones

- **TDD/BDD** — todo código de producción tiene test. Ciclo Rojo → Verde → Refactor
- **Commits** — formato convencional: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`
- **ADRs** — toda decisión arquitectónica significativa se documenta en `docs/adr/`
- **No hay `sigma-core` sin tests** — el dominio es el núcleo del sistema y debe estar cubierto al 100%

---

## Documentación

| Documento | Descripción |
|---|---|
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Principios, capas, componentes y decisiones |
| [`docs/design/DOMAIN-DESIGN.md`](./docs/design/DOMAIN-DESIGN.md) | Modelo de dominio: aggregates, VOs, casos de uso |
| [`docs/design/FIRESTORE-DESIGN.md`](./docs/design/FIRESTORE-DESIGN.md) | Estructura de colecciones, índices y estrategia de escritura |
| [`docs/design/UI-DESIGN.md`](./docs/design/UI-DESIGN.md) | Wireframes y flujos de interfaz |
| [`docs/design/COMMUNICATION-FLOWS.md`](./docs/design/COMMUNICATION-FLOWS.md) | Sequence diagrams de los casos de uso principales |
| [`docs/design/ARCHITECTURE-DIAGRAM.md`](./docs/design/ARCHITECTURE-DIAGRAM.md) | Diagramas completos de arquitectura e infraestructura |
| [`docs/design/API-REST-CATALOGUE.md`](./docs/design/API-REST-CATALOGUE.md) | Contratos de la API REST (endpoints, request/response) |
| [`docs/design/MCP-TOOLS-CATALOGUE.md`](./docs/design/MCP-TOOLS-CATALOGUE.md) | Tools MCP expuestas a Claude |
| [`docs/adr/`](./docs/adr/) | Architecture Decision Records |

---

## Roadmap

### v1 — TaskManagement (en curso)

- [x] Diseño de dominio (Aggregates, VOs, CardFilter)
- [x] ADRs de infraestructura y dominio
- [x] Diseño de API REST y MCP tools
- [ ] Implementación de `sigma-core` (dominio + puertos)
- [ ] Implementación de `sigma-rest` (FastAPI + Firestore)
- [ ] Implementación de `sigma-mcp` (FastMCP)
- [ ] Implementación de `sigma-web` (React PWA)

### v2 — Planning

- [ ] Bounded Context `Planning` (timeboxing, estimaciones, tracking)
- [ ] Integración con Google Calendar
- [ ] Offline support en PWA

---

## Licencia

Proyecto personal. Sin licencia de distribución.
