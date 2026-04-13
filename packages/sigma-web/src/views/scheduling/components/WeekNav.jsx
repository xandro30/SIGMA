import { useState } from 'react';
import { color, font, radius, space, motion } from '../../../shared/tokens';
import { ChevronLeft, ChevronRight, Calendar, Plus } from '../../../shared/components/Icons';
import { formatWeekRange, formatDayTitle, formatMonthTitle } from '../../../shared/dateUtils';
import ViewSelector from './ViewSelector';

export default function WeekNav({
  activeView,
  onViewChange,
  currentDate,
  activeCycle,
  activeCycles,
  onPrev,
  onNext,
  onTemplate,
  onNewBlock,
  showActions = true,
  showNav: showNavProp,
}) {
  const title = getTitle(activeView, currentDate, activeCycle);
  const showNav = showNavProp ?? !activeView.startsWith('cycle:');

  return (
    <div style={{
      height: '48px',
      padding: `0 ${space.lg}`,
      background: color.s1,
      borderBottom: `1px solid ${color.border}`,
      display: 'flex',
      alignItems: 'center',
      gap: space.md,
      flexShrink: 0,
    }}>
      {/* Nav arrows + date */}
      {showNav && (
        <NavButton onClick={onPrev} aria-label="Anterior">
          <ChevronLeft size="16" />
        </NavButton>
      )}

      <h2 style={{
        fontFamily: font.sans,
        fontSize: '18px',
        fontWeight: 700,
        color: color.text,
        margin: 0,
        whiteSpace: 'nowrap',
        letterSpacing: '-0.01em',
        minWidth: 0,
        overflow: 'hidden',
        textOverflow: 'ellipsis',
      }}>
        {title}
      </h2>

      {showNav && (
        <NavButton onClick={onNext} aria-label="Siguiente">
          <ChevronRight size="16" />
        </NavButton>
      )}

      {/* View selector */}
      <div style={{ marginLeft: space.md }}>
        <ViewSelector activeView={activeView} onViewChange={onViewChange} activeCycles={activeCycles} />
      </div>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* Actions — only in day/week views */}
      {showActions && (
        <>
          <ActionButton onClick={onTemplate} variant="secondary">
            <Calendar size="14" />
            <span>Template</span>
          </ActionButton>

          <ActionButton onClick={onNewBlock} variant="primary">
            <Plus size="14" />
            <span>Nuevo bloque</span>
          </ActionButton>
        </>
      )}
    </div>
  );
}

function getTitle(view, date, cycle) {
  if (view.startsWith('cycle:')) {
    if (!cycle) return view.replace('cycle:', '');
    return `${cycle.name} · ${cycle.date_range?.start} — ${cycle.date_range?.end}`;
  }
  switch (view) {
    case 'day': return formatDayTitle(date);
    case 'week': return formatWeekRange(date);
    case 'month': return formatMonthTitle(date);
    default: return formatWeekRange(date);
  }
}

function NavButton({ children, ...props }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        width: '32px',
        height: '32px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: hov ? color.s4 : color.s3,
        border: 'none',
        borderRadius: radius.sm,
        color: color.muted,
        cursor: 'pointer',
        transition: `background ${motion.fast}`,
      }}
      {...props}
    >
      {children}
    </button>
  );
}

function ActionButton({ children, variant = 'secondary', ...props }) {
  const [hov, setHov] = useState(false);
  const isPrimary = variant === 'primary';

  return (
    <button
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: space.xs,
        padding: `${space.sm} ${isPrimary ? space.lg : space.md}`,
        background: isPrimary ? color.yellow : color.s3,
        color: isPrimary ? '#000' : color.text,
        border: 'none',
        borderRadius: radius.md,
        fontFamily: font.sans,
        fontSize: '13px',
        fontWeight: 600,
        whiteSpace: 'nowrap',
        cursor: 'pointer',
        transition: `all ${motion.fast}`,
        ...(hov && !isPrimary && { border: `1px solid ${color.borderAccent}` }),
        ...(!hov && !isPrimary && { border: '1px solid transparent' }),
        ...(hov && isPrimary && { filter: 'brightness(1.1)' }),
        transform: 'scale(1)',
      }}
      onMouseDown={(e) => { e.currentTarget.style.transform = 'scale(0.98)'; }}
      onMouseUp={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}
      {...props}
    >
      {children}
    </button>
  );
}
