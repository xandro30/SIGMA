# UI-DESIGN.md

## SIGMA — Diseño de interfaz de usuario

**Versión:** 1.0
**Fecha:** 2026-03-21

---

## Índice

1. [Sistema de diseño](#1-sistema-de-diseño)
2. [Principios de diseño](#2-principios-de-diseño)
3. [Estructura de navegación](#3-estructura-de-navegación)
4. [Vista de tablero](#4-vista-de-tablero)
5. [Panel de detalle de Card](#5-panel-de-detalle-de-card)
6. [Vista PARA (Áreas y Proyectos)](#6-vista-para-áreas-y-proyectos)
7. [Vista de Epics](#7-vista-de-epics)
8. [Vista de Scheduling](#8-vista-de-scheduling)
9. [Configuración de Space y Workflow](#9-configuración-de-space-y-workflow)
10. [Estados y feedback visual](#10-estados-y-feedback-visual)

## 1. Sistema de diseño

### Paleta de colores

| Token | Valor | Uso |
|---|---|---|
| `color-bg` | `#080808` | Fondo base de la app |
| `color-accent` | `#F5C518` | Acento UI — botones primarios, línea "ahora", highlights |

### Colores de Área

Cada Área tiene asignado uno de los 15 colores del sistema. Los bloques de Scheduling y las cards en el tablero heredan el color de su Área.

| Nombre | Hex |
|---|---|
| Coral | `#E8553E` |
| Violeta | `#8B5CF6` |
| Azul | `#3B82F6` |
| Lima | `#84CC16` |
| Fucsia | `#EC4899` |
| Turquesa | `#14B8A6` |
| Naranja | `#F97316` |
| Ladrillo | `#DC2626` |
| Índigo | `#6366F1` |
| Esmeralda | `#10B981` |
| Ámbar | `#D97706` |
| Miel | `#F59E0B` |
| LimaY | `#A3E635` |
| Dorado | `#B45309` |
| Neón | `#FDE047` |

### Colores de Prioridad

| Prioridad | Color | Hex |
|---|---|---|
| Low | Azul suave | `#60A5FA` |
| Medium | Amarillo | `#FBBF24` |
| High | Naranja | `#F97316` |
| Critical | Rojo | `#EF4444` |

La prioridad se expresa como borde izquierdo de la card en el tablero y como badge en el panel de detalle.

### Tipografía

| Rol | Fuente | Uso |
|---|---|---|
| UI general | DM Sans | Textos, labels, navegación, botones |
| Código / monoespaciado | DM Mono | IDs, fechas, valores técnicos |

---

## 2. Principios de diseño

- **Mobile-first PWA** — la interfaz funciona en móvil y desktop desde el mismo codebase
- **Densidad de información controlada** — el tablero muestra datos suficientes para tomar decisiones sin abrir el detalle
- **Columnas = estados** — la vista de tablero es la vista principal; no hay lista ni kanban alternativo en v1
- **Acciones contextuales** — las acciones disponibles en cada Card dependen de su estado actual
- **Sin modales para operaciones simples** — mover, etiquetar, cambiar prioridad ocurren en línea o en el panel lateral

---

## 3. Estructura de navegación

```
┌─────────────────────────────────────────────────────────────────┐
│  SIGMA                                    [Space selector ▼]    │
├──────────┬──────────────────────────────────────────────────────┤
│          │                                                       │
│  ● Board │  ◄── Vista principal                                  │
│  ○ Areas │                                                       │
│  ○ Epics │                                                       │
│          │                                                       │
│  ──────  │                                                       │
│  ⚙ Space │                                                       │
│          │                                                       │
└──────────┴──────────────────────────────────────────────────────┘
```

**Navegación lateral (sidebar):**
- `Board` — vista de tablero (columnas)
- `Areas` — vista PARA: Áreas → Proyectos → Cards
- `Epics` — agrupaciones de Cards
- `Space settings` — configuración del workflow del Space activo

**Space selector** en la cabecera — cambia el contexto activo. Todas las vistas son relativas al Space seleccionado.

---

## 4. Vista de tablero

Vista principal. Columnas horizontales — pre-workflow fijo a la izquierda, workflow configurable a la derecha.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  SIGMA                                                  [Space: Work ▼]  [+ Card]│
├──────────┬──────────────────────────────────────────────────────────────────────┤
│          │  [🔍 Filtrar]  [Prioridad ▼]  [Área ▼]  [Topic ▼]  [Fecha ▼]         │
│  ● Board ├──────────┬──────────┬──────────┬──────────┬──────────┬───────────────┤
│  ○ Areas │  INBOX   │REFINEMENT│ BACKLOG  │  TO DO   │   WIP    │     DONE      │
│  ○ Epics │          │          │          │  (start) │  ≤3 ★    │    (end)      │
│          ├──────────┼──────────┼──────────┼──────────┼──────────┼───────────────┤
│  ──────  │ ┌──────┐ │ ┌──────┐ │ ┌──────┐ │ ┌──────┐ │ ┌──────┐│               │
│  ⚙ Space │ │ Card │ │ │ Card │ │ │ Card │ │ │ Card │ │ │ Card ││               │
│          │ │title │ │ │title │ │ │title │ │ │title │ │ │title ││               │
│          │ │      │ │ │      │ │ │      │ │ │ due  │ │ │ due  ││               │
│          │ │labels│ │ │labels│ │ │labels│ │ │labels│ │ │labels││               │
│          │ └──────┘ │ └──────┘ │ └──────┘ │ └──────┘ │ └──────┘│               │
│          │          │          │          │          │          │               │
│          │ ┌──────┐ │          │ ┌──────┐ │ ┌──────┐ │          │               │
│          │ │ Card │ │          │ │ Card │ │ │ Card │ │          │               │
│          │ └──────┘ │          │ └──────┘ │ └──────┘ │          │               │
│          │          │          │          │          │          │               │
│          │  [+]     │  [+]     │  [+]     │  [+]     │  [+]    │               │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴───────────────┘
```

**Cabecera de columna:**
- Nombre del estado
- Badge de tipo: `(start)` / `(end)` para los estados del workflow
- Indicador de WIP limit: `≤3 ★` — número máximo y alerta visual si se acerca al límite
- `[+]` al pie — crea Card directamente en esa columna

**Tarjeta en tablero (Card compacta):**

```
┌────────────────────────────────┐
│ ● HIGH   [Epic: Auth]          │  ← prioridad (color) + epic si existe
│                                │
│ Implementar login con Google   │  ← título
│                                │
│ 📅 25 Mar  ░░░░░░▓▓ 6/8       │  ← due date + progreso checklist
│                                │
│ #SecOps #España   IAM  GCP     │  ← labels + topics
└────────────────────────────────┘
```

**Interacciones en tarjeta:**
- `Click` → abre panel de detalle lateral
- `Drag & drop` → mueve entre columnas (valida transiciones en servidor)
- `Right click / long press` → menú contextual: Mover, Archivar, Eliminar

**Barra de filtros:**
Los filtros activos se muestran como chips eliminables. El tablero filtra en tiempo real — solo se muestran las Cards que pasan el `CardFilter` activo.

```
┌─────────────────────────────────────────────────────────┐
│  [🔍]  Prioridad: HIGH, CRITICAL ✕   Área: WORK ✕       │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Panel de detalle de Card

Se abre como panel lateral (slide-in desde la derecha) sin abandonar el tablero.

```
┌──────────────────────────────────────────────────────┐
│  ✕                                          [···]   │
│                                                      │
│  ┌─── ESTADO ──────────────────────────────────┐    │
│  │  [BACKLOG]  →  [TO DO ▼]                    │    │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  Implementar login con Google                        │  ← título editable inline
│                                                      │
│  ┌─── CLASIFICACIÓN ───────────────────────────┐    │
│  │  Prioridad  [HIGH ▼]                        │    │
│  │  Área       [WORK ▼]                        │    │
│  │  Proyecto   [N3 SecOps ▼]                   │    │
│  │  Epic       [Auth Module ▼]                 │    │
│  │  Fecha      [25/03/2026 📅]                 │    │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─── DESCRIPCIÓN ─────────────────────────────┐    │
│  │  Integrar Firebase Auth con el proveedor    │    │
│  │  Google. Scope: email, profile.             │    │
│  │                                        [✏] │    │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─── CHECKLIST  6/8 ██████░░ ─────────────────┐   │
│  │  ✅ Configurar Firebase project              │    │
│  │  ✅ Añadir dependencia firebase-admin        │    │
│  │  ✅ Crear endpoint /auth/callback            │    │
│  │  ✅ Validar ID token en middleware           │    │
│  │  ✅ Test integración                         │    │
│  │  ✅ Documentar flujo                         │    │
│  │  ☐  Review de seguridad                     │    │
│  │  ☐  Deploy a staging                        │    │
│  │                                       [+ item]│   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─── LABELS ──────────────────────────────────┐    │
│  │  [#SecOps] [#España]              [+ label] │    │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─── TOPICS ──────────────────────────────────┐    │
│  │  [IAM] [GCP] [Firebase]           [+ topic] │    │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─── URLS ────────────────────────────────────┐    │
│  │  🔗 Firebase Auth docs                      │    │
│  │  🔗 Jira ticket N3-1234                     │    │
│  │                                        [+ url]│   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  ┌─── CARDS RELACIONADAS ──────────────────────┐    │
│  │  → Configurar Firebase project              │    │
│  │  → Middleware de autenticación              │    │
│  │                                   [+ relacionar]│  │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  [🗑 Eliminar card]                                  │
└──────────────────────────────────────────────────────┘
```

**Menú `[···]`:** Archivar, Duplicar (v2), Copiar enlace.

---

## 6. Vista PARA (Áreas y Proyectos)

Navegación jerárquica: Área → Proyectos → Cards.

```
┌──────────┬──────────────────────────────────────────────────────┐
│          │  ÁREAS Y PROYECTOS                                    │
│  ○ Board │                                                        │
│  ● Areas │  ┌─ WROK ──────────────────────────────────────────┐ │
│  ○ Epics │  │  Plataforma de ciberseguridad para SecOps        │ │
│          │  │  Objetivos: PSOE cert · Chronicle SOAR prod       │ │
│  ──────  │  │                                                    │ │
│  ⚙ Space │  │  ┌── N3 SecOps ─────────────── ACTIVE ──────┐   │ │
│          │  │  │  YARA-L migration + API v1 rollout         │   │ │
│          │  │  │  14 cards activas  ·  2 en WIP             │   │ │
│          │  │  └────────────────────────────────────────────┘   │ │
│          │  │                                                    │ │
│          │  │  ┌── GitSync Automation ─────── ACTIVE ──────┐   │ │
│          │  │  │  Extension Pack promotion via GitSync       │   │ │
│          │  │  │  3 cards activas   ·  1 en WIP              │   │ │
│          │  │  └────────────────────────────────────────────┘   │ │
│          │  │                                         [+ proyecto]│ │
│          │  └────────────────────────────────────────────────────┘ │
│          │                                                        │
│          │  ┌─ Desarrollo personal ───────────────────────────┐ │
│          │  │  Crecimiento técnico y certificaciones           │ │
│          │  │  Objetivos: GCP PCD Q1 · PSOE Q2                │ │
│          │  │                                                    │ │
│          │  │  ┌── GCP PCD 2026 ────────────── ACTIVE ──────┐  │ │
│          │  │  └────────────────────────────────────────────┘  │ │
│          │  └────────────────────────────────────────────────────┘ │
│          │                                              [+ área]  │
└──────────┴──────────────────────────────────────────────────────┘
```

Al hacer click en un Proyecto se filtra el tablero automáticamente mostrando solo las Cards de ese Proyecto.

---

## 7. Vista de Epics

Lista de Epics del Space activo con sus Cards agrupadas.

```
┌──────────┬──────────────────────────────────────────────────────┐
│          │  EPICS                                       [+ epic] │
│  ○ Board │                                                        │
│  ○ Areas │  ┌─ Auth Module ─────────────────────────────────┐   │
│  ● Epics │  │  Sistema de autenticación y autorización       │   │
│          │  │                                                 │   │
│  ──────  │  │  ░░░░████░░░░  6 de 10 cards completadas       │   │
│  ⚙ Space │  │                                                 │   │
│          │  │  ┌──────────────────────┐ ┌──────────────────┐ │   │
│          │  │  │ Implementar login    │ │ Review seguridad  │ │   │
│          │  │  │ [WIP] · HIGH         │ │ [BACKLOG] · HIGH  │ │   │
│          │  │  └──────────────────────┘ └──────────────────┘ │   │
│          │  └────────────────────────────────────────────────┘   │
│          │                                                        │
│          │  ┌─ SOAR Playbooks ──────────────────────────────┐   │
│          │  │  Automatización de respuesta a incidentes       │   │
│          │  │  ░░░░░░░░████  2 de 5 cards completadas        │   │
│          │  └────────────────────────────────────────────────┘   │
└──────────┴──────────────────────────────────────────────────────┘
```

---

## 8. Vista de Scheduling

> **Disponible en v2.** El tablero (v1) y el scheduling (v2) comparten el sistema de colores de Área como hilo conductor visual.

La vista de Scheduling consta de **3 paneles integrados** que se muestran simultáneamente:



**Reglas de la vista:**

- **Bloques heredan color del Área** — GYM es Coral, WORK es Azul, STUDY es Violeta, etc.
- **Cards no son exclusivas de un bloque** — una Card puede continuar en bloques del mismo Área a lo largo del día o la semana
- **Timeline vertical a escala real** — la altura de cada bloque refleja su duración real
- **Línea "ahora"** — marcador en amarillo mostaza () que avanza en tiempo real
- **Panel semana** — vista compacta de ocupación por día; click abre el panel día
- **Panel día** — vista detallada del día seleccionado con todos los bloques
- **Panel detalle de bloque** — cards asignadas al bloque, con opción de arrastrar cards desde el tablero

**Referencia de implementación:** 

---

## 9. Configuración de Space y Workflow

Accesible desde `⚙ Space settings`.

```
┌──────────────────────────────────────────────────────────────────┐
│  CONFIGURACIÓN DE SPACE — Work                                    │
│                                                                   │
│  Nombre del Space  [Work                           ]              │
│                                                                   │
│  ── WORKFLOW ─────────────────────────────────────────────────── │
│                                                                   │
│  [INBOX] → [REFINEMENT] → [BACKLOG] → [TO DO] → [WIP] → [DONE]  │
│                                  fijo ↑           configurable ↑  │
│                                                                   │
│  Estados del workflow:                                            │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  #  Nombre        Tipo      WIP limit   Transiciones       │  │
│  ├────────────────────────────────────────────────────────────┤  │
│  │  1  TO DO         Start     —           → WIP              │  │
│  │  2  WIP           —         ≤3 (todas)  → DONE, → TO DO   │  │
│  │  3  DONE          End       —           —                  │  │
│  ├────────────────────────────────────────────────────────────┤  │
│  │                                            [+ nuevo estado]│  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Click en un estado para editar sus reglas y transiciones         │
│                                                                   │
│  [Guardar cambios]                                                │
└──────────────────────────────────────────────────────────────────┘
```

**Editor de estado (inline al hacer click):**

```
┌─── Editar estado: WIP ─────────────────────────────────────────┐
│                                                                  │
│  Nombre         [WIP                    ]                        │
│  Orden          [2]                                              │
│  Tipo           ○ Normal  ○ Start  ○ End                        │
│                                                                  │
│  Transiciones permitidas                                         │
│  (vacío = todas permitidas)                                      │
│  ☑ TO DO   ☑ DONE   ☐ —                                        │
│                                                                  │
│  WIP Limit rules                                                 │
│  ┌─────────────────────────────────────────────────┐           │
│  │  Máx. cards  [3]   Filtro  [Todas las cards ▼]  │           │
│  │                                          [+ regla]│          │
│  └─────────────────────────────────────────────────┘           │
│                                                                  │
│  [Guardar]  [Cancelar]  [Eliminar estado]                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## 10. Estados y feedback visual

### Indicadores de WIP limit

| Estado | Visual |
|---|---|
| Sin límite | Sin indicador |
| Por debajo del límite | Número en gris: `2/3` |
| Al límite | Número en naranja: `3/3 ⚠` |
| Superado (no debería ocurrir) | Número en rojo: `4/3 ✕` |

### Prioridad (color en tarjeta)

| Prioridad | Color del borde izquierdo |
|---|---|
| `LOW` | Gris |
| `MEDIUM` | Azul |
| `HIGH` | Naranja |
| `CRITICAL` | Rojo |

### Estados de carga y error

- **Optimistic updates:** las acciones del tablero se reflejan inmediatamente en UI; si el servidor falla, se revierte con toast de error
- **Conflicto de WIP limit:** al intentar mover una Card a un estado con límite alcanzado, se muestra un mensaje inline — la Card vuelve a su columna original
- **Offline:** PWA muestra banner de reconexión; operaciones en cola para cuando vuelva la conexión (v2)
