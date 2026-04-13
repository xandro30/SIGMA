# Release: v2-v3 Frontend (Planning BC + Metrics BC)

**Date**: 2026-04-13
**Branch**: `feat/ui-v2-v3-backend`
**Scope**: sigma-web frontend — Schedule + Metrics views

---

## Features

### Schedule View

**Multi-view calendar**
- Day view (single column, navigable by day)
- Week view (7 columns, existing — enhanced with drag-to-create)
- Month view (6x7 grid, click day → day view)
- Sprint view (compact day rows with area-colored bars)
- Cycle overview (Quarter/Semester/Annual: week rows with stacked area bars)
- ViewSelector segmented control: Dia | Semana | Mes | Sprint | Trimestre | Semestre | Año
- Dynamic tabs based on active cycles
- URL deep-linking via useSearchParams

**Drag-to-create**
- Click or drag on WeekGrid/DayView to create time blocks
- 15-minute snap granularity
- Ghost block visual feedback during drag
- Overlap detection (red ghost if collision)
- useDragToCreate hook (reusable)

**Templates CRUD**
- Slide-over panel replacing old TemplateSelector modal
- DayTemplate management: list, create, edit, delete, apply to day
- WeekTemplate management: list, create, assign DayTemplates to weekday slots, apply to week
- time input (any HH:MM) instead of restricted selects
- Replace existing checkbox for week template application

**BlockEditModal improvements**
- Bidirectional duration/end time (change either, the other recalculates)
- Area optional (save blocks without area)
- Date preloading when editing existing blocks
- color-scheme: dark for native datepicker visibility

### Metrics View

**Dashboard redesign (game-stats cards)**
- Overview: global KPIs + AreaCards in responsive grid
- Each AreaCard shows: area name with color, cards done, cycle time, lead time, BulletChart budget
- Click area → Area Detail with KPIs + projects table
- Click project → Project Detail with KPIs + epics table
- Breadcrumb navigation at every level

**KPIs with comparativa**
- KPIRowWithReference: shows local value + delta vs global cycle
- Arrow indicators (▲ slower / ▼ faster) for cycle/lead time
- Cards count with "X en total ciclo" reference

**Data resolution**
- Area names + colors resolved from Areas API
- Project names resolved from Projects API (parallel queries per area)
- Epic names resolved from Epics API
- CycleSelector connected to listCycles (was empty before)

---

## Bugfixes (12)

| Bug | Fix |
|-----|-----|
| Modals/overlays not closing on Escape | useEscapeKey hook applied to 9 components |
| Modal centering broken (scaleIn animation) | scaleInFlex keyframe without translate(-50%,-50%) |
| setState during render in SchedulingSidebarConnected | Moved to useEffect + useCallback |
| CSS border/borderLeft shorthand conflict | Individual border properties in card modals |
| Missing accents (DURACION, AREA, area) | Corrected to DURACIÓN, ÁREA, Sin área |
| Mixed language (CARDS vs ACTIVAS) | Unified to Spanish (TARJETAS) |
| Unclear cycle type abbreviations | SPR/Q → Sprint/Quarter/Semestre/Año |
| CycleSelector empty in Metrics | Connected listCycles API |
| Datepicker invisible in dark mode | color-scheme: dark on inputs |
| Button wrapping on tablet | whiteSpace: nowrap on ActionButton |
| WeekTemplate slot keys wrong | monday→mon (backend format) |
| Week not created before template apply | createWeek before applyTemplate |

---

## Accessibility (WCAG 2.1 AA)

- Global focus-visible outline (2px yellow) for all interactive elements
- BlockEditModal: role="dialog", aria-modal, aria-labelledby, focus trap
- TemplatePanel: role="dialog", ARIA tablist/tab/tabpanel, focus trap
- ViewSelector: aria-current="page" on active view
- MonthView: role="grid", columnheader, row roles, aria-labels on cells
- SprintView: aria-labels on day rows
- CycleOverview: aria-labels on week rows, role="img" on stacked bars
- GhostBlock: role="status", aria-live="polite"
- DayColumn: aria-label with drag instruction

---

## Design System

- Tokens: viewSelector, slideOver, ghost, treeGridColumns, liveBadgeBg, snapshotBadgeBg, scatterDot
- KPI sizing: value 36px, label 12px, 2xl/xl padding
- Grid columns: 240px+100px+100px+100px+160px
- Bullet chart height: 10px
- Keyframes: scaleInFlex, slideInFromRight

---

## Testing

- **93 E2E tests** total (38 scheduling + 29 metrics + 26 others)
- Scheduling: multi-view navigation, escape key, modal fields, template panel
- Metrics: CycleSelector, KPI content, MetricsTree, area data, API validation
- CodeRabbit review: no findings

---

## Data Infrastructure

| Script | Purpose |
|--------|---------|
| `scripts/seed-massive.mjs` | Full workspace: space, areas, projects, epics, cycles, days+blocks, templates |
| `scripts/seed-cards-massive.mjs` | 10K cards with lifecycle at 240 cards/s |
| `scripts/patch-timestamps.mjs` | Realistic cycle/lead times via Firestore patches |
| `scripts/firestore-entrypoint.sh` | Persistence: export-on-exit + conditional import |

---

## Files Changed

- **New**: 20 files (components, hooks, scripts)
- **Modified**: 18 files
- **Deleted**: 1 file (TemplateSelector.jsx, replaced by TemplatePanel)

---

## Known Limitations

- Cycle/lead time data requires timestamp patching (cards created via API have ~0ms between states)
- Firestore emulator persistence requires graceful stop (docker-compose stop -t 30)
- consumed_minutes uses size_mapping estimation, not actual_time from timer
- Projects/epics in metrics tree require cards to have project_id assigned
- Responsive mobile views not implemented for new components
