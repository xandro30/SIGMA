import { useQuery } from '@tanstack/react-query';
import { color, font, space, radius, motion, getAreaHex } from '../../../shared/tokens';
import { addDays, dayNameShort, dayOfMonth, isToday, isWeekend } from '../../../shared/dateUtils';
import { planningApi } from '../../../api/planning';

export default function SprintView({ spaceId, activeCycle, areas, onDayClick }) {
  const startDate = activeCycle?.date_range?.start;
  const endDate = activeCycle?.date_range?.end;

  const { data: daysData } = useQuery({
    queryKey: ['sprintDays', spaceId, startDate, endDate],
    queryFn: () => planningApi.getDaysInRange(spaceId, startDate, endDate),
    enabled: !!spaceId && !!startDate && !!endDate,
  });

  const days = daysData?.days ?? daysData ?? [];
  const daysByDate = {};
  days.forEach(d => { daysByDate[d.date] = d; });

  if (!activeCycle) {
    return (
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', gap: space.lg,
      }}>
        <div style={{
          width: '48px', height: '48px', borderRadius: '12px',
          background: color.yellowDim, display: 'flex',
          alignItems: 'center', justifyContent: 'center', fontSize: '22px',
        }}>
          🏃
        </div>
        <span style={{ fontFamily: font.sans, fontSize: '15px', fontWeight: 600, color: color.text }}>
          Sin sprint activo
        </span>
        <span style={{ fontFamily: font.sans, fontSize: '13px', color: color.muted, textAlign: 'center', maxWidth: '360px' }}>
          Activa un ciclo de tipo Sprint desde el gestor de ciclos para ver la vista de sprint.
        </span>
      </div>
    );
  }

  // Generate all dates in the sprint range
  const sprintDates = [];
  if (startDate && endDate) {
    let current = startDate;
    while (current <= endDate) {
      sprintDates.push(current);
      current = addDays(current, 1);
    }
  }

  const areaMap = {};
  (areas ?? []).forEach(a => { areaMap[a.id] = a; });

  // Calculate max hours for bar scaling
  const maxMinutes = Math.max(1, ...sprintDates.map(d => {
    const dayBlocks = daysByDate[d]?.blocks ?? [];
    return dayBlocks.reduce((s, b) => s + b.duration, 0);
  }));

  return (
    <div style={{
      flex: 1, overflow: 'auto', padding: `${space.lg} ${space.xl}`,
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
        {sprintDates.map(date => {
          const dayBlocks = daysByDate[date]?.blocks ?? [];
          const totalMin = dayBlocks.reduce((s, b) => s + b.duration, 0);
          const today = isToday(date);
          const weekend = isWeekend(date);

          return (
            <button
              key={date}
              onClick={() => onDayClick(date)}
              style={{
                display: 'flex', alignItems: 'center', gap: space.md,
                padding: `${space.sm} ${space.md}`,
                background: today ? color.yellowDim : 'transparent',
                border: today ? `1px solid ${color.borderAccent ?? color.yellow}40` : '1px solid transparent',
                borderRadius: radius.sm, cursor: 'pointer',
                transition: `background ${motion.fast}`,
              }}
            >
              {/* Date label */}
              <div style={{
                width: '80px', flexShrink: 0, display: 'flex',
                alignItems: 'center', gap: space.xs,
              }}>
                <span style={{
                  fontFamily: font.sans, fontSize: '12px', fontWeight: 600,
                  color: today ? color.yellow : weekend ? color.muted2 : color.text,
                }}>
                  {dayNameShort(date)}
                </span>
                <span style={{
                  fontFamily: font.mono, fontSize: '11px',
                  color: today ? color.yellow : color.muted,
                }}>
                  {dayOfMonth(date)}
                </span>
              </div>

              {/* Mini bars */}
              <div style={{
                flex: 1, display: 'flex', gap: '2px', alignItems: 'center',
                height: '20px',
              }}>
                {dayBlocks.map(block => {
                  const area = areaMap[block.area_id];
                  const hex = getAreaHex(area?.color_id);
                  const widthPct = (block.duration / maxMinutes) * 100;
                  return (
                    <div
                      key={block.id}
                      title={`${area?.name ?? 'Sin area'} · ${block.duration}min`}
                      style={{
                        width: `${Math.max(widthPct, 2)}%`,
                        height: '16px',
                        background: `${hex}44`,
                        borderLeft: `2px solid ${hex}`,
                        borderRadius: '2px',
                        flexShrink: 0,
                      }}
                    />
                  );
                })}
                {dayBlocks.length === 0 && (
                  <span style={{ fontFamily: font.mono, fontSize: '10px', color: color.muted2 }}>—</span>
                )}
              </div>

              {/* Total hours */}
              <div style={{
                width: '50px', textAlign: 'right', flexShrink: 0,
                fontFamily: font.mono, fontSize: '10px', color: color.muted2,
              }}>
                {totalMin > 0 ? `${Math.floor(totalMin / 60)}h${totalMin % 60 > 0 ? `${totalMin % 60}m` : ''}` : ''}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
