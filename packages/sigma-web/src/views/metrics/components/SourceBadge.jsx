import { font, radius, space, dashboard } from '../../../shared/tokens';

export default function SourceBadge({ source }) {
  const isLive = source === 'on_demand';
  const dotColor = isLive ? dashboard.liveBadge : dashboard.snapshotBadge;
  const bgColor = isLive ? 'rgba(34,197,94,0.12)' : 'rgba(107,114,128,0.12)';
  const label = isLive ? 'LIVE' : 'SNAPSHOT';

  return (
    <span
      aria-live="polite"
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: space.xs,
        padding: `${space.xs} ${space.sm}`,
        background: bgColor,
        borderRadius: radius.xl,
      }}
    >
      <span style={{
        width: '6px',
        height: '6px',
        borderRadius: '50%',
        background: dotColor,
        flexShrink: 0,
      }} />
      <span style={{
        fontFamily: font.mono,
        fontSize: '10px',
        fontWeight: 700,
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
        color: dotColor,
      }}>
        {label}
      </span>
    </span>
  );
}
