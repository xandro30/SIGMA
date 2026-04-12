import { color, font, calendar, space } from '../../../shared/tokens';

export default function HourLabels() {
  const hours = [];
  for (let h = calendar.startHour; h <= calendar.endHour; h++) {
    hours.push(h);
  }

  return (
    <div style={{ width: calendar.hourLabelWidth, flexShrink: 0 }}>
      {hours.map(h => (
        <div key={h} style={{
          height: calendar.hourHeight,
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'flex-end',
          paddingRight: space.sm,
          paddingTop: '2px',
          fontFamily: font.mono,
          fontSize: '11px',
          color: color.muted2,
          userSelect: 'none',
        }}>
          {String(h).padStart(2, '0')}:00
        </div>
      ))}
    </div>
  );
}
