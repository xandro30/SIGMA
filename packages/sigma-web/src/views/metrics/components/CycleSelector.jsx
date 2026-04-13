import { useState, useRef, useEffect, useCallback } from 'react';
import { color, font, radius, space, elevation, motion } from '../../../shared/tokens';
import { ChevronDown } from '../../../shared/components/Icons';
import SourceBadge from './SourceBadge';
import { useEscapeKey } from '../../../shared/hooks/useEscapeKey';

export default function CycleSelector({ cycles, activeCycleId, onSelect }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  // Close on outside click
  useEffect(() => {
    if (!open) return;
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, [open]);

  const closeDropdown = useCallback(() => setOpen(false), []);
  useEscapeKey(open ? closeDropdown : null);

  const selected = (cycles ?? []).find(c => c.id === activeCycleId);
  const label = selected?.name ?? 'Seleccionar ciclo';

  return (
    <div ref={ref} style={{ position: 'relative' }}>
      {/* Trigger */}
      <button
        onClick={() => setOpen(!open)}
        aria-haspopup="listbox"
        aria-expanded={open}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: space.sm,
          padding: `${space.sm} ${space.md}`,
          background: color.s3,
          border: 'none',
          borderRadius: radius.md,
          fontFamily: font.sans,
          fontSize: '13px',
          fontWeight: 500,
          color: color.text,
          cursor: 'pointer',
          transition: `background ${motion.fast}`,
        }}
      >
        {label}
        <ChevronDown size="14" style={{
          transform: open ? 'rotate(180deg)' : 'rotate(0deg)',
          transition: `transform ${motion.fast}`,
          color: color.muted,
        }} />
      </button>

      {/* Dropdown */}
      {open && (
        <div
          role="listbox"
          style={{
            position: 'absolute',
            top: '100%',
            right: 0,
            marginTop: space.xs,
            minWidth: '260px',
            background: color.s4,
            border: `1px solid ${color.border2}`,
            borderRadius: radius.md,
            boxShadow: elevation[3],
            zIndex: 50,
            overflow: 'hidden',
            animation: 'slideInUp 180ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
          }}
        >
          {(cycles ?? []).map(c => {
            const isActive = c.state === 'active';
            const isSelected = c.id === activeCycleId;
            return (
              <CycleOption
                key={c.id}
                cycle={c}
                isActive={isActive}
                isSelected={isSelected}
                onClick={() => { onSelect(c.id); setOpen(false); }}
              />
            );
          })}
          {(!cycles || cycles.length === 0) && (
            <div style={{ padding: space.lg, fontFamily: font.sans, fontSize: '13px', color: color.muted2, textAlign: 'center' }}>
              Sin ciclos disponibles
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function CycleOption({ cycle, isActive, isSelected, onClick }) {
  const [hov, setHov] = useState(false);

  return (
    <button
      role="option"
      aria-selected={isSelected}
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: space.sm,
        width: '100%',
        padding: `${space.md} ${space.lg}`,
        background: isSelected ? color.yellowDim : (hov ? color.s3 : 'transparent'),
        border: 'none',
        cursor: 'pointer',
        textAlign: 'left',
        transition: `background ${motion.fast}`,
      }}
    >
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontFamily: font.sans, fontSize: '13px', fontWeight: 600, color: color.text }}>
          {cycle.name}
        </div>
        <div style={{ fontFamily: font.mono, fontSize: '10px', color: color.muted2 }}>
          {cycle.date_range?.start} — {cycle.date_range?.end}
        </div>
      </div>
      {isActive && <SourceBadge source="on_demand" />}
    </button>
  );
}
