export const WS = {
  active:    { label: 'En progreso', color: '#3B82F6', bg: '#1a2d4a', icon: '■' },
  waiting:   { label: 'En espera',   color: '#8B5CF6', bg: '#2a1f4a', icon: '▪' },
  done:      { label: 'Completado',  color: '#10B981', bg: '#0d3028', icon: '✓' },
  total:     { label: 'Total',       color: '#F5C518', bg: '#3d2e00', icon: '∑' },
};

// Seed determinista por string → siempre el mismo número para el mismo ID
export function seededRandom(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = ((hash << 5) - hash) + str.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash % 100);
}

// Genera distribución de cards (active+waiting+done suman ≤ total)
export function mockCardCounts(id) {
  const total    = 3 + (Math.abs(seededRandom(id + 't')) % 14);  // 3–16
  const done     = Math.floor(total * (seededRandom(id + 'd') / 100));
  const active   = Math.floor((total - done) * (seededRandom(id + 'a') / 100));
  const waiting  = total - done - active;
  return { total, done, active, waiting };
}
