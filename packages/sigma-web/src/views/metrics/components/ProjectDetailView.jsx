import { color, font, space, radius, dashboard } from '../../../shared/tokens';
import { formatDays } from '../../../shared/dateUtils';
import { KPIRowWithReference } from './KPICard';

export default function ProjectDetailView({ projectId, projectData, projectName, epicsLookup, parentMetrics, globalMetrics }) {
  const m = projectData?.metrics ?? {};
  const epics = Object.entries(projectData?.epics ?? {});

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: space.lg }}>
      {/* Project KPIs — with comparison vs global cycle */}
      <div style={{ padding: `0 ${space['2xl']}` }}>
        <KPIRowWithReference
          metrics={m}
          budgetTotal={null}
          refMetrics={globalMetrics}
          refLabel="ciclo"
        />
      </div>

      {/* Epics table */}
      <div style={{ padding: `0 ${space['2xl']}` }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: dashboard.treeGridColumns,
          padding: `${space.sm} ${space.lg}`,
          borderBottom: `1px solid ${color.border}`,
        }}>
          <span style={headerStyle}>Épica</span>
          <span style={{ ...headerStyle, textAlign: 'right' }}>Cards</span>
          <span style={{ ...headerStyle, textAlign: 'right' }}>Cycle</span>
          <span style={{ ...headerStyle, textAlign: 'right' }}>Lead</span>
          <span style={{ ...headerStyle, textAlign: 'right' }}>Budget</span>
        </div>

        {epics.length === 0 && (
          <div style={{ padding: space.lg, textAlign: 'center', fontFamily: font.sans, fontSize: '13px', color: color.muted2 }}>
            Sin épicas en este proyecto
          </div>
        )}
        {epics.map(([epicId, epicMetrics]) => {
          const epicName = (epicsLookup ?? []).find(e => e.id === epicId)?.name ?? epicId.slice(0, 8);
          return (
            <div key={epicId} style={{
              display: 'grid',
              gridTemplateColumns: dashboard.treeGridColumns,
              padding: `${space.lg} ${space.lg}`,
              borderBottom: `1px solid ${color.border}`,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: space.sm }}>
                <span style={{ fontFamily: font.sans, fontSize: '15px', color: color.muted }}>
                  {epicName}
                </span>
                <span style={{ fontFamily: font.mono, fontSize: '11px', color: color.muted2 }}>epic</span>
              </div>
              <span style={cellStyle}>{epicMetrics.total_cards_completed ?? 0}</span>
              <span style={cellStyle}>{epicMetrics.avg_cycle_time_minutes != null ? formatDays(epicMetrics.avg_cycle_time_minutes) : '—'}</span>
              <span style={cellStyle}>{epicMetrics.avg_lead_time_minutes != null ? formatDays(epicMetrics.avg_lead_time_minutes) : '—'}</span>
              <span style={cellStyle}>{epicMetrics.consumed_minutes ?? 0}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const headerStyle = {
  fontFamily: font.mono,
  fontSize: '11px',
  fontWeight: 700,
  color: color.muted2,
  textTransform: 'uppercase',
  letterSpacing: '0.08em',
  textAlign: 'left',
};

const cellStyle = {
  fontFamily: font.mono,
  fontSize: '14px',
  color: color.text,
  textAlign: 'right',
};
