import { useEffect, useState } from 'react';
import { calendar } from '../../../shared/tokens';

export default function NowIndicator() {
  const [top, setTop] = useState(calcTop());

  useEffect(() => {
    const id = setInterval(() => setTop(calcTop()), 60_000);
    return () => clearInterval(id);
  }, []);

  if (top === null) return null;

  return (
    <div style={{
      position: 'absolute',
      top: `${top}px`,
      left: 0,
      right: 0,
      zIndex: 10,
      pointerEvents: 'none',
      display: 'flex',
      alignItems: 'center',
    }}>
      <div style={{
        width: '8px',
        height: '8px',
        borderRadius: '50%',
        background: calendar.nowLine,
        flexShrink: 0,
        marginLeft: '-4px',
      }} />
      <div style={{
        flex: 1,
        height: '2px',
        background: calendar.nowLine,
      }} />
    </div>
  );
}

function calcTop() {
  const now = new Date();
  const h = now.getHours();
  const m = now.getMinutes();
  if (h < calendar.startHour || h > calendar.endHour) return null;
  return (h - calendar.startHour) * calendar.hourHeightPx + (m / 60) * calendar.hourHeightPx;
}
