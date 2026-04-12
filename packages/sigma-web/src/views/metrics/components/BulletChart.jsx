import { font, dashboard, color } from '../../../shared/tokens';

export default function BulletChart({ consumed, budget, fillColor }) {
  const pct = budget > 0 ? Math.min((consumed / budget) * 100, 100) : 0;
  const overshoot = consumed > budget;
  const fill = overshoot ? dashboard.overshoot : (fillColor ?? dashboard.bulletFill);

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', width: '100%' }}>
      <svg
        width="100%"
        height={dashboard.bulletHeight}
        role="img"
        aria-label={`${consumed} de ${budget} minutos consumidos`}
        style={{ flex: 1, display: 'block' }}
      >
        <rect x="0" y="0" width="100%" height={dashboard.bulletHeight} rx="4" fill={dashboard.bulletBg} />
        <rect x="0" y="0" width={`${pct}%`} height={dashboard.bulletHeight} rx="4" fill={fill} />
      </svg>
      <span style={{
        fontFamily: font.mono,
        fontSize: '10px',
        color: overshoot ? dashboard.overshoot : color.muted,
        whiteSpace: 'nowrap',
        flexShrink: 0,
      }}>
        {consumed}/{budget}
      </span>
    </div>
  );
}
