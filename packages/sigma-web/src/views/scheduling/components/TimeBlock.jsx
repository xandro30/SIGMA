import { useState } from 'react';
import { color, font, radius, space, elevation, motion, calendar } from '../../../shared/tokens';
import { getAreaHex } from '../../../shared/tokens';
import { parseTime } from '../../../shared/dateUtils';

export default function TimeBlock({ block, areaName, areaColorId, onClick }) {
  const [hovered, setHovered] = useState(false);

  const areaHex = getAreaHex(areaColorId);
  const { hour: startH, minute: startM } = parseTime(block.start_at);
  const durationHours = block.duration / 60;
  const endH = startH + Math.floor(block.duration / 60);
  const endM = startM + (block.duration % 60);
  const fmtTime = (h, m) => `${String(h).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`;

  const top = (startH - calendar.startHour) * calendar.hourHeightPx + (startM / 60) * calendar.hourHeightPx;
  const height = Math.max(durationHours * calendar.hourHeightPx, parseInt(calendar.blockMinHeight));

  return (
    <div
      role="gridcell"
      tabIndex={0}
      aria-label={`${areaName ?? 'Sin area'}, ${fmtTime(startH, startM)} a ${fmtTime(endH, endM)}`}
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick?.(); }
      }}
      style={{
        position: 'absolute',
        top: `${top}px`,
        left: space.xs,
        right: space.xs,
        height: `${height}px`,
        background: `${areaHex}22`,
        borderLeft: `3px solid ${areaHex}`,
        borderRadius: radius.sm,
        padding: `${space.xs} ${space.sm}`,
        cursor: 'pointer',
        overflow: 'hidden',
        boxShadow: hovered ? elevation[1] : 'none',
        transform: hovered ? 'scale(1.01)' : 'scale(1)',
        transition: `box-shadow ${motion.fast}, transform ${motion.fast}`,
        zIndex: hovered ? 5 : 1,
      }}
    >
      <div style={{
        fontFamily: font.sans,
        fontSize: '12px',
        fontWeight: 600,
        color: color.text,
        lineHeight: 1.2,
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
      }}>
        {areaName ?? 'Sin area'}
      </div>

      <div style={{
        fontFamily: font.mono,
        fontSize: '11px',
        color: color.muted,
        lineHeight: 1.3,
      }}>
        {fmtTime(startH, startM)}–{fmtTime(endH, endM)}
      </div>

      {block.notes && height > 44 && (
        <div style={{
          fontFamily: font.sans,
          fontSize: '11px',
          color: color.muted2,
          lineHeight: 1.3,
          whiteSpace: 'nowrap',
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          marginTop: '2px',
        }}>
          {block.notes}
        </div>
      )}

      {/* Resize handle */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: '4px',
        cursor: 'ns-resize',
      }} />
    </div>
  );
}
