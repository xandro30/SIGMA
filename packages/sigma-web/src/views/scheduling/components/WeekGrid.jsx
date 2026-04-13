import { useRef, useEffect } from 'react';
import { color, calendar, space } from '../../../shared/tokens';
import { getWeekDates } from '../../../shared/dateUtils';
import HourLabels from './HourLabels';
import DayColumn from './DayColumn';
import DayHeader from './DayHeader';

export default function WeekGrid({ weekStart, days, areas, onBlockClick, dragHandlers, ghostBlock }) {
  const scrollRef = useRef(null);
  const dates = getWeekDates(weekStart);

  // Map days by date for quick lookup
  const daysByDate = {};
  (days ?? []).forEach(d => { daysByDate[d.date] = d; });

  // Scroll to 08:00 on mount
  useEffect(() => {
    if (scrollRef.current) {
      const offset = (8 - calendar.startHour) * calendar.hourHeightPx;
      scrollRef.current.scrollTop = offset;
    }
  }, [weekStart]);

  return (
    <div
      role="grid"
      aria-label="Planificacion semanal"
      style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        background: color.bg,
      }}
    >
      {/* Fixed header row — day names + dates (not scrollable) */}
      <div style={{
        display: 'flex',
        flexShrink: 0,
        borderBottom: `1px solid ${color.border}`,
      }}>
        {/* Spacer for hour labels column */}
        <div style={{ width: calendar.hourLabelWidth, flexShrink: 0 }} />
        {dates.map(date => {
          const dayBlocks = daysByDate[date]?.blocks ?? [];
          const totalMinutes = dayBlocks.reduce((s, b) => s + b.duration, 0);
          return (
            <div key={`hdr-${date}`} style={{ flex: 1, minWidth: 0, borderRight: `1px solid ${color.border}` }}>
              <DayHeader date={date} totalMinutes={totalMinutes} />
            </div>
          );
        })}
      </div>

      {/* Scrollable body — hours + blocks */}
      <div
        ref={scrollRef}
        style={{
          flex: 1,
          display: 'flex',
          overflow: 'auto',
        }}
        onMouseMove={dragHandlers?.handleMouseMove}
        onMouseUp={dragHandlers?.handleMouseUp}
        onMouseLeave={dragHandlers?.handleMouseUp}
      >
        <HourLabels />
        {dates.map(date => (
          <DayColumn
            key={date}
            date={date}
            day={daysByDate[date]}
            areas={areas}
            onBlockClick={onBlockClick}
            onMouseDown={dragHandlers ? (e) => dragHandlers.handleMouseDown(e, date) : undefined}
            ghostBlock={ghostBlock?.dayDate === date ? ghostBlock : null}
          />
        ))}
      </div>
    </div>
  );
}
