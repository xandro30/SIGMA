import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { color, font, space, radius, motion, getAreaHex } from '../../../shared/tokens';
import { getMonthDates, isSameMonth, isToday, isWeekend, dayOfMonth } from '../../../shared/dateUtils';
import { planningApi } from '../../../api/planning';

const WEEKDAY_HEADERS = ['LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB', 'DOM'];

export default function MonthView({ monthDate, spaceId, areas, onDayClick }) {
  const dates = getMonthDates(monthDate);
  const rangeStart = dates[0];
  const rangeEnd = dates[dates.length - 1];

  const { data: daysData } = useQuery({
    queryKey: ['monthDays', spaceId, rangeStart, rangeEnd],
    queryFn: () => planningApi.getDaysInRange(spaceId, rangeStart, rangeEnd),
    enabled: !!spaceId,
  });

  const days = daysData?.days ?? daysData ?? [];
  const daysByDate = {};
  days.forEach(d => { daysByDate[d.date] = d; });

  const areaMap = {};
  (areas ?? []).forEach(a => { areaMap[a.id] = a; });

  // Split into 6 rows of 7
  const rows = [];
  for (let i = 0; i < 42; i += 7) {
    rows.push(dates.slice(i, i + 7));
  }

  return (
    <div style={{
      flex: 1, display: 'flex', flexDirection: 'column',
      overflow: 'hidden', padding: space.lg,
    }}>
      {/* Weekday headers */}
      <div role="row" style={{
        display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)',
        gap: '1px', marginBottom: space.sm,
      }}>
        {WEEKDAY_HEADERS.map(name => (
          <div key={name} role="columnheader" style={{
            textAlign: 'center', fontFamily: font.mono,
            fontSize: '10px', fontWeight: 700, color: color.muted2,
            letterSpacing: '0.08em', padding: `${space.xs} 0`,
          }}>
            {name}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div role="grid" aria-label="Calendario mensual" style={{
        flex: 1, display: 'grid', gridTemplateRows: 'repeat(6, 1fr)',
        gap: '1px',
      }}>
        {rows.map((row, ri) => (
          <div key={ri} role="row" style={{
            display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)',
            gap: '1px',
          }}>
            {row.map(date => {
              const inMonth = isSameMonth(date, monthDate);
              const today = isToday(date);
              const weekend = isWeekend(date);
              const dayBlocks = daysByDate[date]?.blocks ?? [];
              const blockCount = dayBlocks.length;

              return (
                <button
                  key={date}
                  aria-label={`${dayOfMonth(date)}, ${blockCount} bloques`}
                  onClick={() => onDayClick(date)}
                  style={{
                    display: 'flex', flexDirection: 'column',
                    alignItems: 'center', gap: '4px',
                    padding: space.sm,
                    background: today ? color.yellowDim : weekend ? 'rgba(255,255,255,0.02)' : color.s1,
                    border: today ? `1px solid ${color.yellow}60` : `1px solid ${color.border}`,
                    borderRadius: radius.sm,
                    cursor: 'pointer',
                    opacity: inMonth ? 1 : 0.3,
                    transition: `background ${motion.fast}`,
                    minHeight: '60px',
                  }}
                >
                  {/* Day number */}
                  <span style={{
                    fontFamily: font.mono, fontSize: '13px',
                    fontWeight: today ? 700 : 500,
                    color: today ? color.yellow : color.text,
                  }}>
                    {dayOfMonth(date)}
                  </span>

                  {/* Block indicators */}
                  {blockCount > 0 && (
                    <div style={{
                      display: 'flex', gap: '3px', flexWrap: 'wrap',
                      justifyContent: 'center',
                    }}>
                      {dayBlocks.slice(0, 3).map(block => {
                        const area = areaMap[block.area_id];
                        const hex = getAreaHex(area?.color_id);
                        return (
                          <div key={block.id} style={{
                            width: '6px', height: '6px',
                            borderRadius: '50%', background: hex,
                          }} />
                        );
                      })}
                      {blockCount > 3 && (
                        <span style={{
                          fontFamily: font.mono, fontSize: '8px',
                          color: color.muted2,
                        }}>
                          +{blockCount - 3}
                        </span>
                      )}
                    </div>
                  )}
                </button>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}
