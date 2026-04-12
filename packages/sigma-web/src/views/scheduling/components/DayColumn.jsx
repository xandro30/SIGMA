import { color, calendar } from '../../../shared/tokens';
import { isToday, isWeekend } from '../../../shared/dateUtils';
import TimeBlock from './TimeBlock';
import NowIndicator from './NowIndicator';

export default function DayColumn({ date, day, areas, onBlockClick }) {
  const blocks = day?.blocks ?? [];
  const today = isToday(date);
  const weekend = isWeekend(date);
  const totalHours = calendar.endHour - calendar.startHour + 1;

  const areaMap = {};
  (areas ?? []).forEach(a => { areaMap[a.id] = a; });

  return (
    <div style={{
      flex: 1,
      minWidth: 0,
      borderRight: `1px solid ${color.border}`,
      position: 'relative',
      background: weekend ? 'rgba(255,255,255,0.025)' : 'transparent',
    }}>
      {/* Hour grid lines */}
      {Array.from({ length: totalHours }, (_, i) => (
        <div key={i} style={{
          height: calendar.hourHeight,
          borderBottom: `1px solid ${calendar.gridBorder}`,
        }} />
      ))}

      {/* Time blocks positioned absolutely */}
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

      {/* Now indicator only on today */}
      {today && <NowIndicator />}
    </div>
  );
}
