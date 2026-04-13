import { useState } from 'react';
import { color, font, space, radius, motion, dashboard, getAreaHex } from '../../../shared/tokens';
import { ChevronRight } from '../../../shared/components/Icons';
import { formatDays } from '../../../shared/dateUtils';
import { KPIRowWithReference } from './KPICard';
import BulletChart from './BulletChart';

export default function AreaDetailView({ areaId, areaData, areaName, areaColorId, globalMetrics, projectsLookup, epicsLookup, onProjectClick }) {
  const hex = getAreaHex(areaColorId);
  const m = areaData?.metrics ?? {};
  const projects = Object.entries(areaData?.projects ?? {});

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: space.lg }}>
      {/* Area KPIs — with comparison vs global cycle */}
      <div style={{ padding: `0 ${space['2xl']}` }}>
        <KPIRowWithReference
          metrics={m}
          budgetTotal={areaData?.budget_minutes || null}
          refMetrics={globalMetrics}
          refLabel="ciclo"
        />
      </div>

      {/* Projects table */}
      <div style={{ padding: `0 ${space['2xl']}` }}>
        {/* Header */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: dashboard.treeGridColumns,
          padding: `${space.sm} ${space.lg}`,
          borderBottom: `1px solid ${color.border}`,
        }}>
          <span style={headerStyle}>Proyecto</span>
          <span style={{ ...headerStyle, textAlign: 'right' }}>Cards</span>
          <span style={{ ...headerStyle, textAlign: 'right' }}>Cycle</span>
          <span style={{ ...headerStyle, textAlign: 'right' }}>Lead</span>
          <span style={{ ...headerStyle, textAlign: 'right' }}>Budget</span>
        </div>

        {/* Project rows */}
        {projects.length === 0 && (
          <div style={{ padding: space.lg, textAlign: 'center', fontFamily: font.sans, fontSize: '13px', color: color.muted2 }}>
            Sin proyectos en esta área
          </div>
        )}
        {projects.map(([projId, projData]) => {
          const projName = (projectsLookup ?? []).find(p => p.id === projId)?.name ?? projId.slice(0, 8);
          const pm = projData.metrics ?? {};
          return (
            <ProjectRow
              key={projId}
              name={projName}
              metrics={pm}
              onClick={() => onProjectClick(projId)}
            />
          );
        })}
      </div>
    </div>
  );
}

function ProjectRow({ name, metrics, onClick }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        display: 'grid',
        gridTemplateColumns: dashboard.treeGridColumns,
        padding: `${space.lg} ${space.lg}`,
        background: hov ? color.s3 : 'transparent',
        border: 'none',
        borderBottom: `1px solid ${color.border}`,
        cursor: 'pointer',
        textAlign: 'left',
        width: '100%',
        transition: `background ${motion.fast}`,
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: space.sm, minWidth: 0 }}>
        <ChevronRight size="14" style={{ color: color.muted, flexShrink: 0 }} />
        <span style={{ fontFamily: font.sans, fontSize: '15px', fontWeight: 600, color: color.text, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {name}
        </span>
        <span style={{ fontFamily: font.mono, fontSize: '11px', color: color.muted2 }}>project</span>
      </div>
      <span style={cellStyle}>{metrics.total_cards_completed ?? 0}</span>
      <span style={cellStyle}>{metrics.avg_cycle_time_minutes != null ? formatDays(metrics.avg_cycle_time_minutes) : '—'}</span>
      <span style={cellStyle}>{metrics.avg_lead_time_minutes != null ? formatDays(metrics.avg_lead_time_minutes) : '—'}</span>
      <span style={cellStyle}>{metrics.consumed_minutes ?? 0}</span>
    </button>
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
