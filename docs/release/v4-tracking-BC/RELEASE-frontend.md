# v4 Frontend — Release Notes

**Fecha:** 2026-04-15
**Branch:** `feat/ui-v4-tracking-backend`
**Scope:** sigma-web — Tracking UI (Pomodoro), rediseño de cards, Triage unificado, accesibilidad WCAG 2.1 AA.
**Depende de:** v4 Tracking BC (`RELEASE.md` en este mismo directorio).

---

## Features

### Tracking UI — Sesiones Pomodoro en cards

Experiencia completa de seguimiento de trabajo directamente desde el tablero Kanban.

**Footer de tracking en KanbanCard** (tres estados):

| Estado | Visualización |
|--------|---------------|
| Idle | Botón "▶ Start Work" centrado |
| Working | Countdown amarillo `MM:SS`, indicador `ronda/total`, dot pulsante, botón stop |
| Break | Countdown azul `MM:SS`, label "descanso", botón "▶ Reanudar" |

**StartWorkModal**
- Campo de descripción de lo que se va a trabajar
- Selector de configuración Pomodoro: `work_minutes`, `break_minutes`, `num_rounds`
- Defaults: 25/5/4 (Pomodoro estándar)
- Focus trap + cierre con Escape

**StopSessionModal**
- Muestra los minutos trabajados en la sesión actual
- Opciones: guardar en vitácora / descartar

**SessionCompletedBanner**
- Banner inline en la card al completar todas las rondas
- Muestra los minutos totales registrados
- Dismiss manual

**Recuperación de page reload**
- Al recargar, el timer recalcula el tiempo restante desde `current_started_at` (no reinicia)
- Si la sesión ya expiró, llama automáticamente a la transición correspondiente (`complete_round` o `resume_from_break`)

### Vitácora en CardModal

Sección "Vitácora" al final del modal de edición de card.

- Lista de entradas de tiempo con: fecha, descripción y minutos
- Añadir entrada manual (`POST /v1/cards/{card_id}/work-log`): campo descripción + minutos
- Tiempo total acumulado visible
- Orden cronológico inverso (más reciente arriba)

---

## Rediseño de cards

### KanbanCard

Nueva estructura visual implementada en `KanbanBoard.jsx`:

```
┌─────────────────────────────────────────┐
│ [strip tintado: ● ÁREA          [PRIO]] │
│ Título del card                         │
│ Descripción (máx. 3 líneas, si existe)  │
│ Proyecto › Épica (si existen)           │
│ #tag1  #tag2  (si existen)              │
├─────────────────────────────────────────┤
│ footer de tracking                      │
└─────────────────────────────────────────┘
```

- **Strip de área**: fondo tintado `rgba(areaHex, 0.12)`, dot con glow, nombre en uppercase 9px
- **Sin área**: badge de prioridad inline junto al título, variante `xs` (9px)
- **Breadcrumb**: `Proyecto › Épica` con overflow ellipsis en cada segmento
- **Tags**: chips `#tag` en `font.mono`, fondo `rgba(255,255,255,0.05)`
- **Eliminado**: border-left de prioridad (reemplazado por strip + badge)

### TriageView — Unificación visual

Reescritura completa de `TriageView.jsx`:

- `TriageCard` adopta exactamente la misma estructura que `KanbanCard` (strip, breadcrumb, tags)
- Eliminado el panel de detalle lateral ("DETALLE")
- Click en card → `EditCardModal` directamente (igual que Kanban)
- Fetch de épicas/proyectos con el mismo patrón que `WorkspaceLayout`
- Footer de "→ Workflow" solo aparece en cards de stage `backlog`

---

## CreateCardModal — Tags

Campo de etiquetas añadido al modal de creación de cards:

- Input tipo chip: Enter o coma confirman el tag actual
- Backspace elimina el último chip cuando el input está vacío
- `×` elimina chips individuales
- Paste con comas procesa múltiples tags en un solo pegado
- Tags enviados al backend en el campo `labels`

---

## Bugfixes

| Bug | Fix |
|-----|-----|
| Descripción no se guardaba al crear card | Faltaba en `CreateCardCommand`, en `Card.__init__()` y en el router — fix en los 3 niveles |
| Border-top amarillo de columnas desaparecía al arrastrar | CSS shorthand `border` + `borderTop` + `transition: border-color` → propiedades individuales por lado |

---

## Accesibilidad (WCAG 2.1 AA)

| Fix | Criterio | Severidad |
|-----|----------|-----------|
| `role="article"` en wrappers sortables (Kanban + Triage) — los `<button>` de tracking estaban anidados dentro de `role="button"` de dnd-kit | 4.1.2 | Crítico |
| Focus indicator (outline amarillo 2px) en `SortableKanbanCard` y `SortableTriageCard` | 2.4.7 | Mayor |
| `aria-label={card.title}` en wrappers sortables | 4.1.2 | Mayor |
| Touch target mínimo 44×44px en botón "→ Workflow" (TriageView) | 2.5.5 | Mayor |
| `aria-hidden="true"` en área dot decorativo (TriageCard) | 1.3.1 | Menor |
| `aria-hidden="true"` en separador `›` del breadcrumb | 1.3.1 | Menor |

---

## Calidad de código (CodeRabbit)

| Issue | Fix |
|-------|-----|
| `projectById` useMemo con dependencia inestable (`projectResults` array de `useQueries`) | Dep estabilizada con `projectResultsKey` (string de IDs) |
| `DragOverlay` en TriageView pasaba `project={null}` — breadcrumb desaparecía al arrastrar | Derivación correcta igual que en column cards |
| `setTimeout` sin cleanup en toast de error (KanbanBoard + TriageView) | `dragErrorTimerRef` con clearTimeout en `useEffect` cleanup |
| Typo `originalStge` → `originalStage` (TriageView) | Corregido |
| Sin `onError` en mutación `promoteCard` (TriageView) | Añadido con feedback de error en toast |
| `document.getElementById('label-input')` en CreateCardModal | Reemplazado por `useRef` |
| `set(body.labels) if body.labels else set()` (cards.py) | Simplificado a `set(body.labels)` |

---

## Design System — Tokens nuevos

**`src/shared/tokens.js`** — color:
```js
blue:       '#3a7bd5'
blueDim:    'rgba(58,123,213,0.15)'
blueGlow:   'rgba(58,123,213,0.08)'
blueBorder: 'rgba(58,123,213,0.25)'
green:      '#10B981'
greenDim:   'rgba(16,185,129,0.12)'
```

**`src/entities/tracking/trackingTokens.js`** — tokens semánticos de estados:
```js
working: { bg, borderTop, dot }
break:   { bg, borderTop, dot }
```

**`src/index.css`** — keyframe:
```css
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }
```

---

## Backend — Cambios

### Nuevo endpoint

```
POST /v1/cards/{card_id}/work-log    → 204
Body: { description: str, minutes: int (>0) }
```

Registra una entrada manual de tiempo en la vitácora de la card.

### Bugfix

- `POST /v1/spaces/{space_id}/cards` — campo `description` del body ignorado silenciosamente. Fix en router + `CreateCardCommand` + `Card.__init__()`.

---

## Hooks nuevos

| Hook | Propósito |
|------|-----------|
| `useActiveSession(spaceId)` | Polling de la sesión activa del space |
| `useTrackingTimer(initialSeconds, onExpire)` | Countdown con callback al expirar |
| `useStartSession(spaceId)` | Mutation: POST sessions |
| `useStopSession(spaceId)` | Mutation: DELETE sessions |
| `useCompleteRound(spaceId)` | Mutation: POST sessions/rounds |
| `useResumeFromBreak(spaceId)` | Mutation: POST sessions/resume |
| `useWorkLog(cardId)` | Query: GET work-log de una card |
| `useAddWorkLogEntry(cardId)` | Mutation: POST work-log |
| `useFocusTrap(ref, active)` | Shared: focus trap para modales |

---

## Componentes nuevos

| Componente | Ruta |
|------------|------|
| `StartWorkModal` | `shared/components/tracking/StartWorkModal.jsx` |
| `StopSessionModal` | `shared/components/tracking/StopSessionModal.jsx` |
| `SessionCompletedBanner` | `shared/components/tracking/SessionCompletedBanner.jsx` |
| `WorkLogSection` | `shared/components/tracking/WorkLogSection.jsx` (o integrado en CardModal) |

---

## Files Changed

**Nuevos** (frontend): ~14 archivos (hooks, componentes de tracking, API client, tokens de tracking)

**Modificados**:
- `KanbanBoard.jsx` — rediseño + tracking + accesibilidad + quality
- `TriageView.jsx` — reescritura + accesibilidad + quality
- `CreateCardModal.jsx` — tags + useRef + paste
- `PriorityBadge.jsx` — variante `xs`
- `tokens.js` — tokens blue/green
- `index.css` — keyframe pulse
- `EditCardModal.jsx` / `CardModal` — WorkLogSection integrada
- `create_card.py` — bugfix description
- `cards.py` — bugfix description + endpoint work-log + simplificación labels
