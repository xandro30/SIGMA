import { color, font, space, calendar } from '../../../shared/tokens';
import { dayNameShort, dayOfMonth, isToday, isWeekend } from '../../../shared/dateUtils';

export default function DayHeader({ date, totalMinutes = 0 }) {
  const today = isToday(date);
  const weekend = isWeekend(date);
  const hours = Math.floor(totalMinutes / 60);
  const mins = totalMinutes % 60;
  const hoursLabel = mins > 0 ? `${hours}h${mins}m` : `${hours}h`;

  const bg = today
    ? color.yellowDim
    : weekend
      ? 'rgba(255,255,255,0.03)'
      : 'transparent';

  const nameColor = today
    ? color.yellow
    : weekend
      ? color.muted2
      : color.text;

  return (
    <div style={{
      height: calendar.dayHeaderHeight,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '2px',
      borderBottom: today ? `2px solid ${color.yellow}` : `1px solid ${color.border}`,
      background: bg,
      position: 'relative',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'baseline',
        gap: space.xs,
      }}>
        <span style={{
          fontFamily: font.sans,
          fontSize: '12px',
          fontWeight: 600,
          color: nameColor,
        }}>
          {dayNameShort(date)}
        </span>
        <span style={{
          fontFamily: font.mono,
          fontSize: '11px',
          color: today ? color.yellow : color.muted,
        }}>
          {dayOfMonth(date)}
        </span>
      </div>
      {totalMinutes > 0 && (
        <span style={{
          fontFamily: font.mono,
          fontSize: '10px',
          color: color.muted2,
        }}>
          {hoursLabel}
        </span>
      )}
    </div>
  );
}
