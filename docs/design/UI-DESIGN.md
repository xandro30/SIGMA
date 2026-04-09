# UI-DESIGN.md

## SIGMA — Diseño de interfaz de usuario

**Versión:** 1.1
**Fecha:** 2026-03-21
**Última revisión:** 2026-04-09

---

## Índice

1. [Sistema de diseño](#1-sistema-de-diseño)
2. [Principios de diseño](#2-principios-de-diseño)
3. [Estructura de navegación](#3-estructura-de-navegación)
4. [Vistas de tablero](#4-vistas-de-tablero)
5. [Panel de detalle de Card](#5-panel-de-detalle-de-card)
6. [Vistas PARA](#6-vistas-para-áreas-proyectos-epics)
7. [Vista de Epics](#7-vista-de-epics)
8. [Vista de Scheduling](#8-vista-de-scheduling)
9. [Configuración de Space y Workflow](#9-configuración-de-space-y-workflow)
10. [Estados y feedback visual](#10-estados-y-feedback-visual)

## 1. Sistema de diseño

El sistema de diseño está implementado en `sigma-web/src/shared/tokens.js` como objeto de constantes JavaScript importado en todos los componentes.

### Superficies (backgrounds)

| Token | Valor | Uso |
|---|---|---|
| `surface.s1` | `#080808` | Fondo base de la app |
| `surface.s2` | `#111111` | Sidebar, paneles |
| `surface.s3` | `#1a1a1a` | Cards, modales, inputs |
| `surface.s4` | `#222222` | Hover states, elementos elevados |

### Texto

| Token | Valor | Uso |
|---|---|---|
| `text.primary` | `#f0f0f0` | Texto principal |
| `text.muted` | `#888888` | Texto secundario |
| `text.muted2` | `#555555` | Texto terciario, placeholders |

### Acento y bordes

| Token | Valor | Uso |
|---|---|---|
| `color.yellow` | `#F5C518` | Acento UI — botones primarios, selección activa |
| `color.border` | `#2a2a2a` | Bordes de separación por defecto |

### Colores de Prioridad

| Prioridad | Color | Hex |
|---|---|---|
| Low | Azul suave | `#60A5FA` |
| Medium | Amarillo | `#FBBF24` |
| High | Naranja | `#F97316` |
| Critical | Rojo | `#EF4444` |

La prioridad se expresa como borde izquierdo de 4px de la card (tanto en Board como en Triage).

### Colores de Área

Cada Área tiene asignado uno de los 15 colores del sistema mediante `color_id`. El color se usa en el sidebar (ítem activo), en badges y en la cabecera de las vistas de detalle.

| `color_id` | Nombre | Hex |
|---|---|---|
| `coral` | Coral | `#E8553E` |
| `violeta` | Violeta | `#8B5CF6` |
| `azul` | Azul | `#3B82F6` |
| `lima` | Lima | `#84CC16` |
| `fucsia` | Fucsia | `#EC4899` |
| `turquesa` | Turquesa | `#14B8A6` |
| `naranja` | Naranja | `#F97316` |
| `ladrillo` | Ladrillo | `#DC2626` |
| `indigo` | Índigo | `#6366F1` |
| `esmeralda` | Esmeralda | `#10B981` |
| `ambar` | Ámbar | `#D97706` |
| `miel` | Miel | `#F59E0B` |
| `limay` | LimaY | `#A3E635` |
| `dorado` | Dorado | `#B45309` |
| `neon` | Neón | `#FDE047` |

### Elevación y motion

```js
// Elevación (box-shadow)
elevation.low    → sombra sutil para cards
elevation.medium → sombra para modales y paneles flotantes

// Motion (transiciones CSS)
motion.spring    → cubic-bezier(0.34, 1.56, 0.64, 1) — transiciones con rebote
motion.ease      → cubic-bezier(0.25, 0.46, 0.45, 0.94) — transiciones suaves
motion.duration  → 200ms (estándar) / 300ms (modales)

// Radio
radius.sm  → 4px
radius.md  → 8px
radius.lg  → 12px
```

### Tipografía

| Rol | Fuente | Uso |
|---|---|---|
| UI general | DM Sans | Textos, labels, navegación, botones |
| Código / monoespaciado | DM Mono | IDs, fechas, valores técnicos |

### Constantes de dominio en tokens

```js
BEGIN_ID  // UUID reservado para el estado inicial del workflow
FINISH_ID // UUID reservado para el estado final del workflow
```

Estas constantes permiten al frontend identificar estados start/end sin lógica adicional.

---

## 2. Principios de diseño

- **Mobile-first PWA** — la interfaz funciona en móvil y desktop desde el mismo codebase
- **Densidad de información controlada** — el tablero muestra datos suficientes para tomar decisiones sin abrir el detalle
- **Columnas = estados** — la vista de tablero es la vista principal; no hay lista ni kanban alternativo en v1
- **Acciones contextuales** — las acciones disponibles en cada Card dependen de su estado actual
- **Sin modales para operaciones simples** — mover, etiquetar, cambiar prioridad ocurren en línea o en el panel lateral

---

## 3. Estructura de navegación

La navegación implementada combina una **topbar fija** con un **sidebar contextual** que cambia según la vista activa.

### Shell general

```
┌──────────────────────────────────────────────────────────────────────┐
│  [Space ▼]    Board    Triage    Áreas    Schedule    Metrics  [+Card]│ ← Topbar fija
├──────────┬───────────────────────────────────────────────────────────┤
│          │                                                            │
│ Sidebar  │  Contenido principal                                       │
│ (varía   │                                                            │
│ por ruta)│                                                            │
│          │                                                            │
└──────────┴───────────────────────────────────────────────────────────┘
```

### Topbar (`Topbar.jsx`)

Fija en la parte superior. Contiene:
- **Space selector** (izquierda) — dropdown para cambiar el Space activo
- **Navegación principal** (centro) — tabs horizontales
- **`+ Card`** (derecha) — abre `CreateCardModal` globalmente

| Tab | Ruta | Estado |
|---|---|---|
| Board | `/workspace` | Activo |
| Triage | `/triage` | Activo |
| Áreas | `/areas` | Activo |
| Schedule | `/scheduling` | Deshabilitado (v2) |
| Metrics | `/metrics` | Deshabilitado (v3) |

### Sidebar contextual (`Sidebar.jsx`)

El sidebar cambia según la ruta activa:

| Ruta | Sidebar |
|---|---|
| `/triage` | `TriageSidebar` — filtros y opciones del triage |
| `/workspace` | `WorkspaceSidebar` — filtros y opciones del tablero |
| resto | `ParaSidebar` — árbol PARA (Áreas → Proyectos → Epics) |

### Rutas de la aplicación (`App.jsx`)

```
/workspace                                          → Board (WorkflowLayout)
/triage                                             → Triage (TriageView)
/areas                                              → Lista de Áreas
/areas/:areaId                                      → Detalle de Área
/areas/:areaId/projects/:projectId                  → Detalle de Proyecto
/areas/:areaId/projects/:projectId/epics/:epicId    → Detalle de Epic
/spaces/:spaceId/settings                           → Configuración del Space
/scheduling                                         → ComingSoon
/metrics                                            → ComingSoon
```

### CreateCardModal (global)

Se renderiza en `AppShell` y se controla mediante el store Zustand (`createCardOpen`). Se abre desde el botón `+ Card` de la topbar — no está ligado a ninguna ruta en particular.

---

## 4. Vistas de tablero

Hay dos vistas de trabajo independientes: **Board** y **Triage**. Son rutas separadas, no modos de la misma vista.

### 4.1 Board (`/workspace` — `WorkflowLayout`)

Kanban con columnas configurables según el workflow del Space. Scroll horizontal.

```
┌──────────┬──────────┬──────────┬──────────┬──────────┬───────────────┐
│  TO DO   │   WIP    │  REVIEW  │  DONE    │          │               │
│  (start) │  ≤3      │          │  (end)   │          │               │
├──────────┼──────────┼──────────┼──────────┼──────────┼───────────────┤
│ ┌──────┐ │ ┌──────┐ │ ┌──────┐ │          │          │               │
│ │▌Card │ │ │▌Card │ │ │▌Card │ │          │          │               │
│ │title │ │ │title │ │ │title │ │          │          │               │
│ └──────┘ │ └──────┘ │ └──────┘ │          │          │               │
│ ┌──────┐ │          │          │          │          │               │
│ │▌Card │ │          │          │          │          │               │
│ └──────┘ │          │          │          │          │               │
└──────────┴──────────┴──────────┴──────────┴──────────┴───────────────┘
```

El borde izquierdo coloreado (`▌`) indica la prioridad de cada card.

Las columnas se generan dinámicamente a partir de los `WorkflowState` del Space activo. Los estados con `BEGIN_ID` y `FINISH_ID` se marcan visualmente como start/end.

### 4.2 Triage (`/triage` — `TriageView`)

Tres columnas **fijas** correspondientes al pre-workflow. No es configurable — siempre son Inbox, Refinement y Backlog.

```
┌──────────────┬────────────────┬──────────────────┐
│    INBOX     │  REFINEMENT    │     BACKLOG       │
├──────────────┼────────────────┼──────────────────┤
│ ┌──────────┐ │ ┌──────────┐  │ ┌──────────────┐  │
│ │▌ Card    │ │ │▌ Card    │  │ │▌ Card        │  │
│ │  título  │ │ │  título  │  │ │  título      │  │
│ └──────────┘ │ └──────────┘  │ └──────────────┘  │
│ ┌──────────┐ │               │                   │
│ │▌ Card    │ │               │                   │
│ └──────────┘ │               │                   │
└──────────────┴────────────────┴──────────────────┘
```

**Interacción en TriageView:**
- `Click` en card → abre panel de detalle lateral (sin cambiar ruta)
- Botón editar en panel → abre `EditCardModal`
- El borde izquierdo de 4px usa el color de prioridad

### 4.3 Card compacta (ambas vistas)

```
┌────────────────────────────────────┐
│▌ Implementar login con Google      │  ← borde izquierdo = prioridad
│                                    │
│  📅 25 Mar    [Auth Module]         │  ← due date + epic badge
│  #SecOps  #España                  │  ← labels
└────────────────────────────────────┘
```

El borde izquierdo es de 4px y usa `borderLeft` como propiedad explícita (no el shorthand `border`) para evitar conflictos de reconciliación con el borde de selección.

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

## 6. Vistas PARA (Áreas, Proyectos, Epics)

La jerarquía PARA se navega mediante rutas independientes, no como overlay del tablero. El `ParaSidebar` actúa como árbol de navegación cuando se está en cualquier ruta que no sea `/workspace` ni `/triage`.

### ParaSidebar

Árbol de navegación PARA mostrado en el sidebar cuando la ruta activa es `/areas/*`:

```
Áreas
  ├── Work  ●────────────  (color del área)
  │   ├── N3 SecOps
  │   │   ├── Auth Module  ← Epic
  │   │   └── SOAR Core    ← Epic
  │   └── GitSync
  └── Personal
      └── GCP PCD 2026
```

El ítem activo del sidebar se colorea con el color del Área correspondiente (`color_id`).

### Vista AreaList (`/areas`)

Lista de todas las Áreas. Cada área muestra nombre, descripción y recuento de proyectos.

### Vista AreaDetail (`/areas/:areaId`)

Detalle de un Área con sus Proyectos listados. Muestra objetivos (texto libre) y lista de proyectos con su estado.

### Vista ProjectDetail (`/areas/:areaId/projects/:projectId`)

Detalle de un Proyecto con sus Epics listadas. Muestra los Epics del proyecto con nombre y descripción.

### Vista EpicDetail (`/areas/:areaId/projects/:projectId/epics/:epicId`)

Detalle de un Epic. Muestra las Cards asociadas al Epic.

### CreateCardModal y clasificación PARA

El modal de creación incluye selección jerarquizada:

```
Área  [selector]
  └── Epic  [selector — filtrado por área, agrupado por proyecto]
              ├── Proyecto A
              │   ├── Epic 1
              │   └── Epic 2
              └── Proyecto B
                  └── Epic 3
```

Al seleccionar un Epic, `project_id` se propaga automáticamente desde el Epic seleccionado. Las Epics se obtienen mediante el endpoint `GET /areas/{area_id}/epics`.

### EditCardModal

Mismo comportamiento que CreateCardModal para la selección de Epic. Usa `useEpicsByArea(areaId)` y `useProjects(areaId)` para construir la lista agrupada en el `<select>` con `<optgroup>` por proyecto.

---

## 7. Vista de Epics

> **Nota de implementación (v1):** No existe una vista de Epics independiente en la navegación principal. Los Epics se acceden a través de la jerarquía PARA: `Áreas → Proyecto → Epics`. La vista diseñada aquí es la planificación para cuando se añada una vista dedicada.

Los Epics pertenecen a un Proyecto (y por extensión a un Área) — no al Space directamente. El tab `Epics` del diseño original se eliminó de la topbar en favor de la navegación jerárquica PARA.

La vista de detalle de Epic (`/areas/:areaId/projects/:projectId/epics/:epicId`) muestra:
- Nombre y descripción del Epic
- Cards asociadas al Epic

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
│                                                                  │
│  Transiciones permitidas                                         │
│  ☑ TO DO   ☑ DONE   ☐ —                                        │
│                                                                  │
│  [Guardar]  [Cancelar]  [Eliminar estado]                        │
└──────────────────────────────────────────────────────────────────┘
```

**Nota:** Los estados Start y End no se configuran con un tipo explícito. Se determinan mediante UUIDs reservados (`BEGIN_ID`, `FINISH_ID`) definidos en el dominio. La configuración del workflow guarda solo `{id, name, order}` por estado, más el array de transiciones.

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

| Prioridad | Color del borde izquierdo | Hex |
|---|---|---|
| `LOW` | Azul suave | `#60A5FA` |
| `MEDIUM` | Amarillo | `#FBBF24` |
| `HIGH` | Naranja | `#F97316` |
| `CRITICAL` | Rojo | `#EF4444` |

### Estados de carga y error

- **Optimistic updates:** las acciones del tablero se reflejan inmediatamente en UI; si el servidor falla, se revierte con toast de error
- **Conflicto de WIP limit:** al intentar mover una Card a un estado con límite alcanzado, se muestra un mensaje inline — la Card vuelve a su columna original
- **Offline:** PWA muestra banner de reconexión; operaciones en cola para cuando vuelva la conexión (v2)
