import { useRef, useEffect } from 'react';
import { color, calendar, space, font } from '../../../shared/tokens';
import { isToday, isWeekend, formatDayTitle } from '../../../shared/dateUtils';
import HourLabels from './HourLabels';
import TimeBlock from './TimeBlock';
import NowIndicator from './NowIndicator';
import GhostBlock from './GhostBlock';

export default function DayView({ date, day, areas, onBlockClick, dragHandlers, ghostBlock }) {
  const scrollRef = useRef(null);
  const blocks = day?.blocks ?? [];
  const today = isToday(date);
  const weekend = isWeekend(date);
  const totalHours = calendar.endHour - calendar.startHour + 1;

  const areaMap = {};
  (areas ?? []).forEach(a => { areaMap[a.id] = a; });

  // Scroll to 08:00 on mount
  useEffect(() => {
    if (scrollRef.current) {
      const offset = (8 - calendar.startHour) * calendar.hourHeightPx;
      scrollRef.current.scrollTop = offset;
    }
  }, [date]);

  return (
    <div
      role="grid"
      aria-label={`Planificacion ${formatDayTitle(date)}`}
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        background: color.bg,
      }}
    >
      {/* Scrollable body */}
      <div
        ref={scrollRef}
        style={{
          flex: 1,
          display: 'flex',
          overflow: 'auto',
        }}
      >
        <HourLabels />
        <div
          style={{
            flex: 1,
            position: 'relative',
            borderRight: `1px solid ${color.border}`,
            borderLeft: `1px solid ${color.border}`,
            background: weekend ? 'rgba(255,255,255,0.025)' : 'transparent',
            cursor: 'crosshair',
          }}
          onMouseDown={dragHandlers ? (e) => dragHandlers.handleMouseDown(e, date) : undefined}
          onMouseMove={dragHandlers?.handleMouseMove}
          onMouseUp={dragHandlers?.handleMouseUp}
        >
          {/* Hour grid lines */}
          {Array.from({ length: totalHours }, (_, i) => (
            <div key={i} style={{
              height: calendar.hourHeight,
              borderBottom: `1px solid ${calendar.gridBorder}`,
            }} />
          ))}

          {/* Time blocks */}
          {blocks.map(block => {
            const area = areaMap[block.area_id];
            return (
              <TimeBlock
                key={block.id}
                block={block}
                areaName={area?.name}
                areaColorId={area?.color_id}
                onClick={() => onBlockClick?.(day, block)}
              />
            );
          })}

          {/* Ghost block during drag */}
          {ghostBlock && ghostBlock.dayDate === date && (
            <GhostBlock
              top={ghostBlock.top}
              height={ghostBlock.height}
              label={ghostBlock.label}
              hasOverlap={ghostBlock.hasOverlap}
            />
          )}

          {/* Now indicator */}
          {today && <NowIndicator />}
        </div>
      </div>
    </div>
  );
}
