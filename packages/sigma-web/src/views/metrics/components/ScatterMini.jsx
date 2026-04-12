import { useState } from 'react';
import { color, font, radius, space, elevation } from '../../../shared/tokens';

export default function ScatterMini({ entries }) {
  const [tooltip, setTooltip] = useState(null);

  if (!entries || entries.length === 0) return null;

  const W = 160, H = 100;
  const maxEst = Math.max(...entries.map(e => e.estimated_minutes), 1);
  const maxAct = Math.max(...entries.map(e => e.actual_minutes), 1);
  const maxVal = Math.max(maxEst, maxAct) * 1.1; // 10% padding

  const scaleX = (v) => (v / maxVal) * W;
  const scaleY = (v) => H - (v / maxVal) * H;

  const avgBias = entries.length > 0
    ? Math.round((entries.reduce((s, e) => s + (e.actual_minutes - e.estimated_minutes), 0) / entries.length / maxVal) * 100)
    : 0;

  return (
    <div style={{ position: 'relative', display: 'inline-block' }}>
      <svg
        width={W}
        height={H}
        role="img"
        aria-label={`Calibracion: ${entries.length} cards, sesgo medio ${avgBias > 0 ? '+' : ''}${avgBias}%`}
        style={{ display: 'block' }}
      >
        {/* Reference line: perfect estimation diagonal */}
        <line
          x1={0} y1={H}
          x2={W} y2={0}
          stroke={color.muted2}
          strokeDasharray="4 3"
          strokeWidth="1"
        />

        {/* Data points */}
        {entries.map((e, i) => (
          <circle
            key={i}
            cx={scaleX(e.estimated_minutes)}
            cy={scaleY(e.actual_minutes)}
            r={tooltip === i ? 6 : 4}
            fill="rgba(245,197,24,0.6)"
            style={{ cursor: 'pointer', transition: 'r 120ms' }}
            onMouseEnter={() => setTooltip(i)}
            onMouseLeave={() => setTooltip(null)}
          />
        ))}
      </svg>

      {/* Tooltip */}
      {tooltip !== null && entries[tooltip] && (
        <div style={{
          position: 'absolute',
          top: scaleY(entries[tooltip].actual_minutes) - 36,
          left: scaleX(entries[tooltip].estimated_minutes),
          transform: 'translateX(-50%)',
          background: color.s4,
          borderRadius: radius.xs,
          padding: `${space.xs} ${space.sm}`,
          boxShadow: elevation[2],
          whiteSpace: 'nowrap',
          pointerEvents: 'none',
          zIndex: 20,
        }}>
          <span style={{ fontFamily: font.mono, fontSize: '10px', color: color.text }}>
            Est: {entries[tooltip].estimated_minutes}min, Real: {entries[tooltip].actual_minutes}min
          </span>
        </div>
      )}
    </div>
  );
}
