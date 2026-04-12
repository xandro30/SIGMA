import { color, font, radius, space, elevation, dashboard } from '../../../shared/tokens';
import { formatDays } from '../../../shared/dateUtils';
import BulletChart from './BulletChart';

export default function KPICard({ label, value, subtitle, bullet }) {
  return (
    <div style={{
      minWidth: dashboard.kpiCardMinWidth,
      background: color.s2,
      borderRadius: radius.lg,
      boxShadow: elevation[1],
      padding: space.lg,
      display: 'flex',
      flexDirection: 'column',
      gap: space.sm,
    }}>
      <span style={{
        fontFamily: font.mono,
        fontSize: dashboard.kpiLabelSize,
        fontWeight: 700,
        textTransform: 'uppercase',
        letterSpacing: '0.08em',
        color: color.muted2,
      }}>
        {label}
      </span>

      <span style={{
        fontFamily: font.sans,
        fontSize: dashboard.kpiValueSize,
        fontWeight: 700,
        color: color.text,
        lineHeight: 1.1,
      }}>
        {value}
      </span>

      {subtitle && (
        <span style={{
          fontFamily: font.sans,
          fontSize: '11px',
          color: color.muted,
        }}>
          {subtitle}
        </span>
      )}

      {bullet && (
        <BulletChart consumed={bullet.consumed} budget={bullet.budget} />
      )}
    </div>
  );
}

/** Render the 4 KPI cards from a global MetricsBlock. */
export function KPIRow({ metrics, budgetTotal }) {
  const ct = metrics.avg_cycle_time_minutes;
  const lt = metrics.avg_lead_time_minutes;

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: space.lg,
    }}>
      <KPICard
        label="Cards completadas"
        value={metrics.total_cards_completed}
        subtitle="este ciclo"
      />
      <KPICard
        label="Cycle time medio"
        value={ct != null ? formatDays(ct) : '—'}
        subtitle="entered → done"
      />
      <KPICard
        label="Lead time medio"
        value={lt != null ? formatDays(lt) : '—'}
        subtitle="created → done"
      />
      <KPICard
        label="Budget consumido"
        value={`${metrics.consumed_minutes}min`}
        bullet={budgetTotal ? { consumed: metrics.consumed_minutes, budget: budgetTotal } : null}
      />
    </div>
  );
}
