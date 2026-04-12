import { color, font, space } from '../../../shared/tokens';
import SourceBadge from './SourceBadge';
import CycleSelector from './CycleSelector';

export default function MetricsHeader({ metrics, cycles, activeCycleId, onCycleChange }) {
  return (
    <div style={{
      padding: `${space.xl} ${space['2xl']}`,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'flex-start',
      flexWrap: 'wrap',
      gap: space.lg,
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: space.xs }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: space.md }}>
          <h1 style={{
            fontFamily: font.sans,
            fontSize: '22px',
            fontWeight: 800,
            color: color.text,
            margin: 0,
            letterSpacing: '-0.02em',
          }}>
            Metrics
          </h1>
          {metrics && <SourceBadge source={metrics.source} />}
        </div>
        {metrics?.date_range && (
          <span style={{
            fontFamily: font.sans,
            fontSize: '13px',
            color: color.muted,
          }}>
            {metrics.date_range.start} — {metrics.date_range.end}
          </span>
        )}
      </div>

      <CycleSelector
        cycles={cycles}
        activeCycleId={activeCycleId}
        onSelect={onCycleChange}
      />
    </div>
  );
}
