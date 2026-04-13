import { color, font, space, dashboard } from '../../../shared/tokens';
import MetricsRow from './MetricsRow';

export default function MetricsTree({ areas }) {
  if (!areas || Object.keys(areas).length === 0) {
    return (
      <div style={{
        padding: space['2xl'],
        textAlign: 'center',
        fontFamily: font.sans,
        fontSize: '13px',
        color: color.muted2,
      }}>
        Sin datos por área en este ciclo
      </div>
    );
  }

  // Column headers
  const headerStyle = {
    fontFamily: font.mono,
    fontSize: '10px',
    fontWeight: 700,
    color: color.muted2,
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
    textAlign: 'right',
  };

  return (
    <div role="tree" aria-label="Metricas por area">
      {/* Header row */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: dashboard.treeGridColumns,
        padding: `${space.sm} ${space.lg}`,
        borderBottom: `1px solid ${color.border}`,
      }}>
        <span style={{ ...headerStyle, textAlign: 'left' }}>Entidad</span>
        <span style={headerStyle}>Cards</span>
        <span style={headerStyle}>Cycle</span>
        <span style={headerStyle}>Lead</span>
        <span style={headerStyle}>Budget</span>
      </div>

      {/* Area rows */}
      {Object.entries(areas).map(([areaId, areaData]) => (
        <MetricsRow
          key={areaId}
          name={areaData.area_id ?? areaId}
          type="area"
          level={1}
          areaColorId={null}
          metrics={areaData.metrics}
          budget={areaData.budget_minutes}
          children={
            Object.entries(areaData.projects ?? {}).map(([projId, projData]) => (
              <MetricsRow
                key={projId}
                name={projData.project_id ?? projId}
                type="project"
                level={2}
                metrics={projData.metrics}
                children={
                  Object.entries(projData.epics ?? {}).map(([epicId, epicMetrics]) => (
                    <MetricsRow
                      key={epicId}
                      name={epicId}
                      type="epic"
                      level={3}
                      metrics={epicMetrics}
                    />
                  ))
                }
              />
            ))
          }
        />
      ))}
    </div>
  );
}
