import { priority, font } from '../tokens';
export default function PriorityBadge({ value, size = 'sm' }) {
  const p   = priority[value] ?? priority.low;
  const pad = size === 'md' ? '4px 11px' : size === 'xs' ? '2px 6px' : '3px 8px';
  const fs  = size === 'md' ? '11px' : size === 'xs' ? '9px' : '10px';
  return (
    <span style={{
      fontSize: fs, fontWeight: 700,
      color: p.color,
      background: p.bg,
      border: `1px solid ${p.color}40`,
      borderRadius: '5px', padding: pad,
      fontFamily: font.mono,
      whiteSpace: 'nowrap', flexShrink: 0,
      letterSpacing: '0.06em',
    }}>
      {p.label}
    </span>
  );
}
