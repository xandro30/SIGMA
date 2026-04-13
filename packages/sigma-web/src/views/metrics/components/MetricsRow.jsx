import { useState } from 'react';
import { color, font, space, motion, dashboard, getAreaHex } from '../../../shared/tokens';
import { formatDays } from '../../../shared/dateUtils';
import { ChevronRight } from '../../../shared/components/Icons';
import ScatterMini from './ScatterMini';
import BulletChart from './BulletChart';

export default function MetricsRow({ name, type, level, areaColorId, metrics, budget, children }) {
  const [expanded, setExpanded] = useState(false);
  const [hovered, setHovered] = useState(false);
  const hasChildren = children && children.length > 0;
  const hasCal = metrics.calibration_entries?.length > 0;
  const indent = level * dashboard.indentStep;

  return (
    <div>
      <div
        role="treeitem"
        aria-expanded={hasChildren ? expanded : undefined}
        aria-level={level + 1}
        tabIndex={0}
        onClick={() => hasChildren && setExpanded(!expanded)}
        onKeyDown={(e) => {
          if (e.key === 'ArrowRight' && hasChildren) setExpanded(true);
          if (e.key === 'ArrowLeft') setExpanded(false);
          if (e.key === 'Enter') setExpanded(!expanded);
        }}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          display: 'grid',
          gridTemplateColumns: dashboard.treeGridColumns,
          alignItems: 'center',
          minHeight: '44px',
          padding: `${space.sm} ${space.lg}`,
          paddingLeft: `${parseInt(space.lg) + indent}px`,
          background: hovered ? color.s3 : 'transparent',
          cursor: hasChildren ? 'pointer' : 'default',
          transition: `background ${motion.fast}`,
          borderBottom: level === 1 ? `1px solid ${color.border}` : 'none',
        }}
      >
        {/* Name cell */}
        <div style={{ display: 'flex', alignItems: 'center', gap: space.sm, minWidth: 0 }}>
          {/* Chevron */}
          {hasChildren ? (
            <span style={{
              display: 'flex',
              transform: expanded ? 'rotate(90deg)' : 'rotate(0deg)',
              transition: `transform ${motion.fast}`,
              color: color.muted,
              flexShrink: 0,
            }}>
              <ChevronRight size="14" />
            </span>
          ) : (
            <span style={{ width: '14px', flexShrink: 0 }} />
          )}

          {/* Area color dot (only for area level) */}
          {areaColorId && (
            <span style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: getAreaHex(areaColorId),
              flexShrink: 0,
            }} />
          )}

          <span style={{
            fontFamily: font.sans,
            fontSize: '14px',
            fontWeight: 600,
            color: level >= 3 ? color.muted : color.text,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}>
            {name}
          </span>

          <span style={{
            fontFamily: font.mono,
            fontSize: '11px',
            color: color.muted2,
            flexShrink: 0,
          }}>
            {type}
          </span>
        </div>

        {/* Metrics cells */}
        <span style={{ fontFamily: font.mono, fontSize: '13px', fontWeight: 500, color: color.text, textAlign: 'right' }}>
          {metrics.total_cards_completed}
        </span>
        <span style={{ fontFamily: font.mono, fontSize: '13px', fontWeight: 500, color: color.text, textAlign: 'right' }}>
          {formatDays(metrics.avg_cycle_time_minutes)}
        </span>
        <span style={{ fontFamily: font.mono, fontSize: '13px', fontWeight: 500, color: color.text, textAlign: 'right' }}>
          {formatDays(metrics.avg_lead_time_minutes)}
        </span>
        <div style={{ textAlign: 'right' }}>
          {budget != null ? (
            <BulletChart consumed={metrics.consumed_minutes} budget={budget} fillColor={areaColorId ? getAreaHex(areaColorId) : undefined} />
          ) : (
            <span style={{ fontFamily: font.mono, fontSize: '13px', fontWeight: 500, color: color.text }}>
              {metrics.consumed_minutes}
            </span>
          )}
        </div>
      </div>

      {/* Expanded: calibration scatter + children */}
      {expanded && (
        <div style={{ animation: 'slideInUp 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards' }}>
          {hasCal && (
            <div style={{ paddingLeft: `${parseInt(space.lg) + indent + 28}px`, paddingBottom: space.md }}>
              <ScatterMini entries={metrics.calibration_entries} />
            </div>
          )}
          {children}
        </div>
      )}
    </div>
  );
}
