# ARCHITECTURE-DIAGRAM.md

## SIGMA — Diagrama de arquitectura completo

**Versión:** 1.0
**Fecha:** 2026-03-21

---

## Índice

1. [Vista de sistema completo](#1-vista-de-sistema-completo)
2. [Vista de capas y dependencias](#2-vista-de-capas-y-dependencias)
3. [Vista de infraestructura GCP](#3-vista-de-infraestructura-gcp)
4. [Vista de dominio](#4-vista-de-dominio)
5. [Vista de despliegue](#5-vista-de-despliegue)

---

## 1. Vista de sistema completo

Todos los actores, componentes y dependencias en un único diagrama de referencia.

```mermaid
flowchart TD
    %% Actores externos
    Dev(["👤 Desarrollador"])
    Claude(["🤖 Claude\n(agente IA)"])

    %% Clientes
    subgraph CLIENTS ["Clientes"]
        PWA["sigma-web\nPWA React\n(Firebase Hosting)"]
    end

    %% Adaptadores de entrada
    subgraph ADAPTERS_IN ["Adaptadores de entrada"]
        REST["sigma-rest\nFastAPI\n(Cloud Run)"]
        MCP["sigma-mcp\nFastMCP\n(Cloud Run)"]
    end

    %% Dominio
    subgraph CORE ["sigma-core (dominio puro)"]
        direction TB
        UC["Casos de uso\n(Commands + Queries)"]
        DOM["Dominio\n(Aggregates · Entities · VOs)"]
        PORTS["Puertos\n(Protocols)"]
        UC --> DOM
        UC --> PORTS
    end

    %% Adaptadores de salida
    subgraph ADAPTERS_OUT ["Adaptadores de salida (Firestore)"]
        CARD_R["CardRepository\nimpl."]
        SPACE_R["SpaceRepository\nimpl."]
        AREA_R["AreaRepository\nimpl."]
        PROJ_R["ProjectRepository\nimpl."]
        EPIC_R["EpicRepository\nimpl."]
    end

    %% Infraestructura GCP
    subgraph GCP ["Google Cloud Platform"]
        FS[("Firestore")]
        SM["Secret Manager"]
        FA["Firebase Auth"]
        AR["Artifact Registry"]
        CR_R["Cloud Run\n(sigma-rest)"]
        CR_M["Cloud Run\n(sigma-mcp)"]
        FH["Firebase Hosting"]
    end

    %% Conexiones de actores
    Dev -->|"browser / mobile"| PWA
    Claude -->|"MCP protocol\n(Streamable HTTP)"| MCP

    %% Conexiones cliente → adaptador
    PWA -->|"HTTP REST\nBearer token"| REST
    PWA -->|"Firebase SDK"| FA

    %% Conexiones adaptadores → core
    REST --> UC
    MCP --> UC

    %% Conexiones core → adaptadores de salida
    PORTS -.->|"implementado por"| CARD_R
    PORTS -.->|"implementado por"| SPACE_R
    PORTS -.->|"implementado por"| AREA_R
    PORTS -.->|"implementado por"| PROJ_R
    PORTS -.->|"implementado por"| EPIC_R

    %% Adaptadores de salida → Firestore
    CARD_R --> FS
    SPACE_R --> FS
    AREA_R --> FS
    PROJ_R --> FS
    EPIC_R --> FS

    %% Infraestructura de soporte
    REST -->|"verifica token"| FA
    REST -->|"lee secretos"| SM
    MCP -->|"lee secretos"| SM
    AR -->|"imagen Docker"| CR_R
    AR -->|"imagen Docker"| CR_M
    FH -->|"sirve"| PWA

    %% Despliegue
    REST -.->|"desplegado en"| CR_R
    MCP -.->|"desplegado en"| CR_M
```

---

## 2. Vista de capas y dependencias

Regla fundamental: **las dependencias solo apuntan hacia el interior**. El dominio no conoce nada externo.

```mermaid
flowchart LR
    subgraph L1 ["Capa 1 — Clientes"]
        PWA["sigma-web\n(React PWA)"]
        CLAUDE["Claude\n(agente)"]
    end

    subgraph L2 ["Capa 2 — Adaptadores de entrada"]
        REST["sigma-rest\nFastAPI"]
        MCP_A["sigma-mcp\nFastMCP"]
    end

    subgraph L3 ["Capa 3 — Aplicación (sigma-core)"]
        direction TB
        UC["use_cases/\nCommands y Queries"]
        subgraph L3b ["Dominio puro"]
            AGG["Aggregates\nCard · Space"]
            ENT["Entidades\nArea · Project · Epic"]
            VO["Value Objects\nCardId · Url · ..."]
            FILTER["CardFilter\nMotor de predicados"]
            ERR["Errores de dominio"]
        end
        PROT["ports/\nProtocols (interfaces)"]
    end

    subgraph L4 ["Capa 4 — Adaptadores de salida"]
        REPO["Repositorios\nFirestore impl."]
    end

    subgraph L5 ["Capa 5 — Infraestructura"]
        FS[("Firestore")]
        FA["Firebase Auth"]
        SM["Secret Manager"]
    end

    PWA -->|REST| REST
    CLAUDE -->|MCP| MCP_A
    REST --> UC
    MCP_A --> UC
    UC --> L3b
    UC --> PROT
    PROT -.->|implementa| REPO
    REPO --> FS
    REST --> FA
    REST & MCP_A --> SM

    style L3 fill:#e8f4f8,stroke:#2196F3
    style L3b fill:#fff,stroke:#90CAF9
```

---

## 3. Vista de infraestructura GCP

Todos los recursos GCP con sus relaciones y el free tier de cada uno.

```mermaid
flowchart TD
    subgraph INTERNET ["Internet"]
        USER(["👤 Usuario"])
        CLAUDE(["🤖 Claude"])
    end

    subgraph GCP ["Google Cloud Project — sigma"]

        subgraph HOSTING ["Firebase (Hosting + Auth)"]
            FH["Firebase Hosting\n📦 sigma-web PWA\n✓ Free: 10GB"]
            FA["Firebase Auth\n🔐 Google OAuth\n✓ Free: ilimitado"]
        end

        subgraph COMPUTE ["Compute (Cloud Run)"]
            CR1["Cloud Run — sigma-rest\n🐳 Docker container\n✓ Free: 2M req/mes\n⚡ min instances: 0"]
            CR2["Cloud Run — sigma-mcp\n🐳 Docker container\n✓ Free: 2M req/mes\n⚡ min instances: 0"]
        end

        subgraph DATA ["Data"]
            FS[("Firestore\n📄 Base de datos\n✓ Free: 50K reads/día\n         20K writes/día")]
        end

        subgraph SECURITY ["Security & Config"]
            SM["Secret Manager\n🔑 Credenciales\n✓ Free: 6 versiones"]
        end

        subgraph REGISTRY ["Container Registry"]
            AR["Artifact Registry\n📦 Imágenes Docker\n✓ Free: 0.5GB"]
        end

    end

    USER -->|"HTTPS"| FH
    USER -->|"HTTPS (API)"| CR1
    CLAUDE -->|"MCP / HTTPS"| CR2

    FH -->|"REST API calls"| CR1
    CR1 -->|"verifica JWT"| FA
    CR1 -->|"lee/escribe"| FS
    CR2 -->|"lee/escribe"| FS
    CR1 -->|"lee secretos en arranque"| SM
    CR2 -->|"lee secretos en arranque"| SM
    AR -->|"pull en deploy"| CR1
    AR -->|"pull en deploy"| CR2
```

---

## 4. Vista de dominio

Aggregates, entidades y sus relaciones en el Bounded Context TaskManagement.

```mermaid
classDiagram
    class Space {
        +SpaceId id
        +SpaceName name
        +WorkflowState[] workflow_states
        +get_start_state()
        +get_end_state()
        +is_valid_transition()
        +add_state()
        +remove_state()
    }

    class WorkflowState {
        +WorkflowStateId id
        +string name
        +int order
        +bool is_start
        +bool is_end
        +WipLimitRule[] wip_limit_rules
        +frozenset allowed_transitions
    }

    class Card {
        +CardId id
        +SpaceId space_id
        +CardTitle title
        +PreWorkflowStage pre_workflow_stage
        +WorkflowStateId workflow_state_id
        +Priority priority
        +string[] labels
        +string[] topics
        +Url[] urls
        +ChecklistItem[] checklist
        +CardId[] related_cards
        +move_to_workflow_state()
        +move_to_pre_workflow()
    }

    class Area {
        +AreaId id
        +string name
        +string description
        +string[] objectives
    }

    class Project {
        +ProjectId id
        +string name
        +string description
        +string[] objectives
        +AreaId area_id
        +ProjectStatus status
    }

    class Epic {
        +EpicId id
        +SpaceId space_id
        +string name
        +string description
    }

    class CardFilter {
        +StringPredicate title
        +ListPredicate labels
        +ListPredicate topics
        +DatePredicate due_date
        +matches(card) bool
    }

    class WipLimitRule {
        +int max_cards
        +CardFilter filter
    }

    Space "1" *-- "many" WorkflowState : contiene
    WorkflowState "1" *-- "many" WipLimitRule : tiene
    WipLimitRule "1" --> "0..1" CardFilter : filtra con
    Card "many" --> "1" Space : pertenece a
    Card "many" --> "0..1" Area : clasificada en
    Card "many" --> "0..1" Project : clasificada en
    Card "many" --> "0..1" Epic : agrupada en
    Project "many" --> "1" Area : pertenece a
    Epic "many" --> "1" Space : pertenece a
```

---

## 5. Vista de despliegue

Cómo los componentes se empaquetan y despliegan.

```mermaid
flowchart LR
    subgraph REPO ["Repositorio (mono-repo)"]
        CORE_SRC["sigma-core/\nsrc/"]
        REST_SRC["sigma-rest/\nsrc/"]
        MCP_SRC["sigma-mcp/\nsrc/"]
        WEB_SRC["sigma-web/\nsrc/"]
    end

    subgraph BUILD ["Build"]
        CORE_PKG["sigma-core\n(Python package)"]
        REST_IMG["sigma-rest\n(Docker image)"]
        MCP_IMG["sigma-mcp\n(Docker image)"]
        WEB_DIST["sigma-web\n(Static bundle)"]
    end

    subgraph DEPLOY ["Deploy (GCP)"]
        AR_REST["Artifact Registry\nsigma-rest:tag"]
        AR_MCP["Artifact Registry\nsigma-mcp:tag"]
        CR_REST["Cloud Run\nsigma-rest"]
        CR_MCP["Cloud Run\nsigma-mcp"]
        FH_DEPLOY["Firebase Hosting\nsigma-web"]
    end

    CORE_SRC --> CORE_PKG
    REST_SRC --> REST_IMG
    CORE_PKG -->|"uv workspace dep"| REST_IMG
    MCP_SRC --> MCP_IMG
    CORE_PKG -->|"uv workspace dep"| MCP_IMG
    WEB_SRC --> WEB_DIST

    REST_IMG --> AR_REST
    MCP_IMG --> AR_MCP
    AR_REST --> CR_REST
    AR_MCP --> CR_MCP
    WEB_DIST --> FH_DEPLOY

    note1["⚠ CI/CD pipeline pendiente de definir.\nCada componente se despliega\nde forma independiente."]

    style note1 fill:#fff9c4,stroke:#f9a825
```

> **Nota sobre CI/CD:** el pipeline de integración y despliegue continuo queda fuera del alcance de v1. Cuando se defina, cada componente (`sigma-rest`, `sigma-mcp`, `sigma-web`) tendrá su propio pipeline de build, test y deploy independiente, reflejando los ciclos de despliegue separados establecidos en ADR-001.
