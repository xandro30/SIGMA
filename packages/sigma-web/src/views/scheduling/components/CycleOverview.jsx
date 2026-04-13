import { useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { color, font, space, radius, motion, getAreaHex } from '../../../shared/tokens';
import { addDays, getMonday, getWeekNumber, dayOfMonth, formatWeekRange } from '../../../shared/dateUtils';
import { planningApi } from '../../../api/planning';

/**
 * Overview for Quarter / Semester / Annual cycles.
 * Rows = weeks, bars = hours per area (segmented, colored).
 * Click on a week row → navigate to that week in Week view.
 */
export default function CycleOverview({ spaceId, cycle, areas, onWeekClick }) {
  const startDate = cycle?.date_range?.start;
  const endDate = cycle?.date_range?.end;

  // Query must start from the Monday of the first week (cycle start may be mid-week)
  const queryStart = startDate ? getMonday(startDate) : null;
  // End on the Sunday of the last week
  const lastMonday = endDate ? getMonday(endDate) : null;
  const queryEnd = lastMonday ? addDays(lastMonday, 6) : null;

  const { data: daysData } = useQuery({
    queryKey: ['cycleDays', spaceId, queryStart, queryEnd],
    queryFn: () => planningApi.getDaysInRange(spaceId, queryStart, queryEnd),
    enabled: !!spaceId && !!queryStart && !!queryEnd,
  });

  const days = daysData?.days ?? daysData ?? [];

  const areaMap = useMemo(() => {
    const m = {};
    (areas ?? []).forEach(a => { m[a.id] = a; });
    return m;
  }, [areas]);

  // Group days into weeks
  const weeks = useMemo(() => {
    if (!startDate || !endDate) return [];

    // Build weeks from Monday to Sunday covering the cycle range
    const result = [];
    let weekMonday = getMonday(startDate);

    while (weekMonday <= endDate) {
      const weekSunday = addDays(weekMonday, 6);
      const weekDates = [];
      for (let i = 0; i < 7; i++) {
        weekDates.push(addDays(weekMonday, i));
      }

      // Collect all blocks for this week
      const weekBlocks = [];
      weekDates.forEach(date => {
        const day = days.find(d => d.date === date);
        if (day?.blocks) {
          weekBlocks.push(...day.blocks);
        }
      });

      // Aggregate hours per area
      const areaHours = {};
      let totalMinutes = 0;
      weekBlocks.forEach(b => {
        const key = b.area_id ?? '__none__';
        areaHours[key] = (areaHours[key] ?? 0) + b.duration;
        totalMinutes += b.duration;
      });

      result.push({
        monday: weekMonday,
        sunday: weekSunday,
        weekNumber: getWeekNumber(weekMonday),
        areaHours,
        totalMinutes,
      });

      weekMonday = addDays(weekMonday, 7);
    }

    return result;
  }, [startDate, endDate, days]);

  // Max for bar scaling
  const maxMinutes = Math.max(1, ...weeks.map(w => w.totalMinutes));

  if (!cycle) {
    return (
      <div style={{
        flex: 1, display: 'flex', flexDirection: 'column',
        alignItems: 'center', justifyContent: 'center', gap: space.lg,
      }}>
        <span style={{ fontFamily: font.sans, fontSize: '15px', fontWeight: 600, color: color.text }}>
          Sin ciclo activo de este tipo
        </span>
        <span style={{ fontFamily: font.sans, fontSize: '13px', color: color.muted, textAlign: 'center', maxWidth: '360px' }}>
          Activa un ciclo desde el gestor de ciclos para ver el overview.
        </span>
      </div>
    );
  }

  return (
    <div style={{
      flex: 1, overflow: 'auto', padding: `${space.lg} ${space.xl}`,
    }}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
        {weeks.map(week => {
          const barWidthPct = week.totalMinutes > 0
            ? (week.totalMinutes / maxMinutes) * 100
            : 0;
          const totalHours = Math.floor(week.totalMinutes / 60);
          const totalMins = week.totalMinutes % 60;
          const hoursLabel = week.totalMinutes > 0
            ? `${totalHours}h${totalMins > 0 ? totalMins + 'm' : ''}`
            : '';

          // Get sorted area segments for the stacked bar
          const segments = Object.entries(week.areaHours)
            .sort((a, b) => b[1] - a[1]) // largest first
            .map(([areaId, minutes]) => {
              const area = areaMap[areaId];
              const hex = areaId === '__none__' ? '#6B7280' : getAreaHex(area?.color_id);
              return { areaId, minutes, hex, name: area?.name ?? 'Sin area' };
            });

          return (
            <button
              key={week.monday}
              onClick={() => onWeekClick(week.monday)}
              style={{
                display: 'flex', alignItems: 'center', gap: space.md,
                padding: `${space.sm} ${space.md}`,
                background: 'transparent',
                border: '1px solid transparent',
                borderRadius: radius.sm, cursor: 'pointer',
                transition: `background ${motion.fast}`,
              }}
              onMouseEnter={e => { e.currentTarget.style.background = color.s2; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; }}
            >
              {/* Week label */}
              <div style={{
                width: '160px', flexShrink: 0, display: 'flex',
                flexDirection: 'column', gap: '2px',
              }}>
                <span style={{
                  fontFamily: font.sans, fontSize: '12px', fontWeight: 600,
                  color: color.text,
                }}>
                  S{week.weekNumber}
                </span>
                <span style={{
                  fontFamily: font.mono, fontSize: '10px', color: color.muted2,
                }}>
                  {dayOfMonth(week.monday)}–{dayOfMonth(week.sunday)}
                </span>
              </div>

              {/* Stacked bar */}
              <div style={{
                flex: 1, display: 'flex', alignItems: 'center',
                height: '28px', gap: 0,
              }}>
                {segments.length > 0 ? (
                  <div style={{
                    display: 'flex', height: '24px',
                    width: `${Math.max(barWidthPct, 3)}%`,
                    borderRadius: '4px', overflow: 'hidden',
                  }}>
                    {segments.map(seg => {
                      const segPct = (seg.minutes / week.totalMinutes) * 100;
                      const segHours = Math.floor(seg.minutes / 60);
                      const segMins = seg.minutes % 60;
                      const label = segHours > 0
                        ? `${segHours}h${segMins > 0 ? segMins : ''}`
                        : `${segMins}m`;

                      return (
                        <div
                          key={seg.areaId}
                          title={`${seg.name}: ${label}`}
                          style={{
                            width: `${segPct}%`,
                            minWidth: '20px',
                            height: '100%',
                            background: `${seg.hex}55`,
                            borderLeft: `2px solid ${seg.hex}`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            overflow: 'hidden',
                          }}
                        >
                          {seg.minutes >= 30 && (
                            <span style={{
                              fontFamily: font.mono, fontSize: '9px',
                              fontWeight: 700, color: seg.hex,
                              whiteSpace: 'nowrap',
                            }}>
                              {label}
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <span style={{ fontFamily: font.mono, fontSize: '10px', color: color.muted2 }}>—</span>
                )}
              </div>

              {/* Total */}
              <div style={{
                width: '50px', textAlign: 'right', flexShrink: 0,
                fontFamily: font.mono, fontSize: '10px', color: color.muted2,
              }}>
                {hoursLabel}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
