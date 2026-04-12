import { useState, useEffect } from 'react';
import { color, font, space, radius, dashboard, motion } from '../../tokens';
import { getAreaHex } from '../../tokens';
import { formatWeekRange, formatDuration } from '../../dateUtils';
import { X, Clock } from '../Icons';

export default function SchedulingSidebar({ weekStart, week, days, areas, cycle, onNotesChange, onClearTemplate, onManageCycle }) {
  const [notes, setNotes] = useState(week?.notes ?? '');

  useEffect(() => { setNotes(week?.notes ?? ''); }, [week?.notes]);

  // Calculate hours by area
  const allBlocks = (days ?? []).flatMap(d => d.blocks ?? []);
  const totalMinutes = allBlocks.reduce((sum, b) => sum + b.duration, 0);
  const byArea = {};
  allBlocks.forEach(b => {
    const key = b.area_id ?? '_none';
    byArea[key] = (byArea[key] ?? 0) + b.duration;
  });
  const maxMinutes = Math.max(...Object.values(byArea), 1);

  const areaMap = {};
  (areas ?? []).forEach(a => { areaMap[a.id] = a; });

  return (
    <div style={{ padding: space.lg, display: 'flex', flexDirection: 'column', gap: space.xl }}>

      {/* Cycle status — most important, always visible */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: space.sm }}>
        <SectionLabel>Ciclo</SectionLabel>
        {cycle ? (
          <button
            onClick={onManageCycle}
            style={{
              display: 'flex', alignItems: 'center', gap: space.sm,
              padding: space.md, background: color.s2, border: `1px solid ${color.border}`,
              borderRadius: radius.md, cursor: 'pointer', textAlign: 'left',
              transition: `all ${motion.fast}`, width: '100%',
            }}
            onMouseEnter={e => { e.currentTarget.style.borderColor = color.borderAccent; }}
            onMouseLeave={e => { e.currentTarget.style.borderColor = color.border; }}
          >
            <Clock size="14" style={{ color: color.muted, flexShrink: 0 }} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ fontFamily: font.sans, fontSize: '12px', fontWeight: 600, color: color.text, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {cycle.name}
              </div>
              <div style={{ fontFamily: font.mono, fontSize: '10px', color: color.muted2 }}>
                {cycle.state === 'active' ? '● Activo' : cycle.state === 'draft' ? '○ Borrador' : '◼ Cerrado'}
              </div>
            </div>
          </button>
        ) : (
          <button
            onClick={onManageCycle}
            style={{
              padding: space.md, background: color.yellowDim,
              border: `1px dashed ${color.borderAccent}`, borderRadius: radius.md,
              cursor: 'pointer', fontFamily: font.sans, fontSize: '12px',
              fontWeight: 600, color: color.yellow, width: '100%',
              transition: `all ${motion.fast}`,
            }}
          >
            + Crear ciclo
          </button>
        )}
      </div>

      {/* Week label */}
      <SectionLabel>
        {weekStart ? formatWeekRange(weekStart) : 'SEMANA'}
      </SectionLabel>

      {/* Notes */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: space.xs }}>
        <SectionLabel>Notas</SectionLabel>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          onBlur={() => { if (notes !== (week?.notes ?? '')) onNotesChange?.(notes); }}
          rows={3}
          placeholder="Notas de la semana..."
          style={{ resize: 'vertical', fontSize: '12px' }}
        />
      </div>

      {/* Applied template */}
      {week?.applied_template_id && (
        <div style={{ display: 'flex', alignItems: 'center', gap: space.sm }}>
          <span style={{ fontFamily: font.sans, fontSize: '12px', color: color.muted, flex: 1 }}>
            Template aplicada
          </span>
          <button
            onClick={onClearTemplate}
            style={{ background: 'none', border: 'none', color: color.muted2, cursor: 'pointer', padding: '2px' }}
            aria-label="Limpiar template"
          >
            <X size="14" />
          </button>
        </div>
      )}

      {/* Hours planned */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: space.sm }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
          <SectionLabel>Horas planificadas</SectionLabel>
          <span style={{ fontFamily: font.mono, fontSize: '13px', fontWeight: 600, color: color.text }}>
            {formatDuration(totalMinutes)}
          </span>
        </div>

        {Object.entries(byArea).map(([areaId, minutes]) => {
          const area = areaMap[areaId];
          const areaHex = area ? getAreaHex(area.color_id) : color.muted2;
          const pct = (minutes / maxMinutes) * 100;
          return (
            <div key={areaId} style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                <span style={{ fontFamily: font.sans, fontSize: '11px', color: color.muted }}>
                  {area?.name ?? 'Sin area'}
                </span>
                <span style={{ fontFamily: font.mono, fontSize: '11px', color: color.muted2 }}>
                  {formatDuration(minutes)}
                </span>
              </div>
              <div style={{ height: '6px', background: dashboard.bulletBg, borderRadius: radius.xs, overflow: 'hidden' }}>
                <div style={{ width: `${pct}%`, height: '100%', background: areaHex, borderRadius: radius.xs, transition: `width 380ms cubic-bezier(0.16, 1, 0.3, 1)` }} />
              </div>
            </div>
          );
        })}

        {totalMinutes === 0 && (
          <p style={{ fontFamily: font.sans, fontSize: '12px', color: color.muted2, fontStyle: 'italic' }}>
            Sin bloques esta semana
          </p>
        )}
      </div>
    </div>
  );
}

function SectionLabel({ children }) {
  return (
    <span style={{
      fontFamily: font.mono,
      fontSize: '10px',
      fontWeight: 700,
      color: color.muted2,
      textTransform: 'uppercase',
      letterSpacing: '0.1em',
    }}>
      {children}
    </span>
  );
}
