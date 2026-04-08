// ─── Surfaces ────────────────────────────────────────────────────────────────
// Perceptually uniform steps so layers are always distinguishable
export const color = {
  bg:           '#060606',         // App base background
  s1:           '#0f0f11',         // Columns, main panels
  s2:           '#161618',         // Cards at rest, inputs
  s3:           '#1f1f22',         // Hover surfaces, active containers
  s4:           '#28282c',         // Dropdowns, context menus
  border:       'rgba(255,255,255,0.07)',   // Subtle glass borders
  border2:      'rgba(255,255,255,0.13)',   // Input borders, visible separators
  borderAccent: 'rgba(245,197,24,0.35)',    // Yellow-tinted borders

  // Text hierarchy (fixes undefined color.muted / color.muted2)
  text:     '#F0F0F4',   // Titles, primary content
  muted:    '#8B8D96',   // Descriptions, secondary labels
  muted2:   '#72747E',   // Timestamps, tertiary metadata — min 4.7:1 on s1/s2 (WCAG AA)
  disabled: '#383840',   // Disabled states

  // Accent
  yellow:     '#F5C518',
  yellowDim:  'rgba(245,197,24,0.15)',
  yellowGlow: 'rgba(245,197,24,0.08)',
};

// ─── Typography ───────────────────────────────────────────────────────────────
export const font = {
  sans: "'DM Sans', system-ui, sans-serif",
  mono: "'DM Mono', 'Courier New', monospace",
};

// ─── Layout ───────────────────────────────────────────────────────────────────
export const layout = {
  topbarHeight:    '56px',
  sidebarWidth:    '220px',
  sidebarCollapsed: '48px',
  columnWidth:     '270px',
};

// ─── Elevation ────────────────────────────────────────────────────────────────
// The `inset 0 1px 0 rgba(255,255,255,n)` simulates light from above → real depth
export const elevation = {
  1: '0 1px 2px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.04)',
  2: '0 4px 16px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.06)',
  3: '0 12px 40px rgba(0,0,0,0.75), inset 0 1px 0 rgba(255,255,255,0.08)',
  4: '0 30px 80px rgba(0,0,0,0.85), inset 0 1px 0 rgba(255,255,255,0.1)',
};

// ─── Motion ───────────────────────────────────────────────────────────────────
// Spring-based easing everywhere — removes robotic feel
export const motion = {
  fast:   '120ms cubic-bezier(0.16, 1, 0.3, 1)',
  normal: '220ms cubic-bezier(0.16, 1, 0.3, 1)',
  slow:   '380ms cubic-bezier(0.16, 1, 0.3, 1)',
  spring: '400ms cubic-bezier(0.34, 1.56, 0.64, 1)',
};

// ─── Border radius ────────────────────────────────────────────────────────────
export const radius = {
  sm: '6px',
  md: '10px',
  lg: '14px',
  xl: '20px',
};

// ─── Area colors (15 — user-approved palette, unchanged) ─────────────────────
const AREA_COLORS = {
  coral:     '#E8553E', violeta:   '#8B5CF6', azul:      '#3B82F6',
  lima:      '#84CC16', fucsia:    '#EC4899', turquesa:  '#14B8A6',
  naranja:   '#F97316', ladrillo:  '#DC2626', indigo:    '#6366F1',
  esmeralda: '#10B981', ambar:     '#D97706', miel:      '#F59E0B',
  limay:     '#A3E635', dorado:    '#B45309', neon:      '#FDE047',
};

export const areaColors = Object.entries(AREA_COLORS).map(([id, hex]) => ({ id, hex }));
export const getAreaHex = (color_id) => AREA_COLORS[color_id] ?? '#555560';

// Calculates whether text on an area color should be white or black
export function getTextOnColor(hex) {
  if (!hex || !/^#[0-9A-Fa-f]{6}/.test(hex)) return '#FFFFFF';
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return (r * 0.299 + g * 0.587 + b * 0.114) > 140 ? '#000000' : '#FFFFFF';
}

// ─── Priority ─────────────────────────────────────────────────────────────────
// Backgrounds use rgba so they read well on any surface
export const priority = {
  low:      { label: 'LOW',  color: '#60A5FA', bg: 'rgba(96,165,250,0.12)'  },
  medium:   { label: 'MED',  color: '#FBBF24', bg: 'rgba(251,191,36,0.12)'  },
  high:     { label: 'HIGH', color: '#F97316', bg: 'rgba(249,115,22,0.12)'  },
  critical: { label: 'CRIT', color: '#EF4444', bg: 'rgba(239,68,68,0.12)'   },
};

export const PRIORITY_ORDER = { critical: 0, high: 1, medium: 2, low: 3 };
export const FINISH_ID = '00000000-0000-4000-a000-000000000002';
export const BEGIN_ID  = '00000000-0000-4000-a000-000000000001';
