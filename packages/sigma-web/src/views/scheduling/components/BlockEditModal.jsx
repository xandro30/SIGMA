import { useState, useRef, useEffect } from 'react';
import { color, font, radius, space, elevation, motion, overlay } from '../../../shared/tokens';
import { X } from '../../../shared/components/Icons';
import { useEscapeKey } from '../../../shared/hooks/useEscapeKey';

function toDatetimeLocal(isoStr) {
  if (!isoStr) return '';
  const d = new Date(isoStr);
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const min = String(d.getMinutes()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}T${hh}:${min}`;
}

function addMinutesToDatetimeLocal(dtLocal, minutes) {
  if (!dtLocal) return '';
  const d = new Date(dtLocal);
  d.setMinutes(d.getMinutes() + minutes);
  return toDatetimeLocal(d.toISOString());
}

function diffMinutes(startDtLocal, endDtLocal) {
  if (!startDtLocal || !endDtLocal) return 0;
  const a = new Date(startDtLocal);
  const b = new Date(endDtLocal);
  return Math.max(5, Math.round((b - a) / 60000));
}

export default function BlockEditModal({ block, areas, onSave, onDelete, onClose }) {
  useEscapeKey(onClose);

  // Focus trap (WCAG 2.4.3)
  const modalRef = useRef(null);
  useEffect(() => {
    const modal = modalRef.current;
    if (!modal) return;
    const focusable = modal.querySelectorAll('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
    if (focusable.length === 0) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    first.focus();
    const trap = (e) => {
      if (e.key !== 'Tab') return;
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };
    modal.addEventListener('keydown', trap);
    return () => modal.removeEventListener('keydown', trap);
  }, []);

  const isNew = !block?.id;
  const [startAt, setStartAt] = useState(() => toDatetimeLocal(block?.start_at));
  const [duration, setDuration] = useState(block?.duration ?? 60);
  const [areaId, setAreaId] = useState(block?.area_id ?? '');
  const [notes, setNotes] = useState(block?.notes ?? '');
  const [endAt, setEndAt] = useState(() => addMinutesToDatetimeLocal(toDatetimeLocal(block?.start_at), block?.duration ?? 60));

  const handleStartChange = (value) => {
    setStartAt(value);
    // Recalculate end from new start + current duration
    if (value) setEndAt(addMinutesToDatetimeLocal(value, duration));
  };

  const handleDurationChange = (value) => {
    const mins = Math.max(5, Number(value) || 0);
    setDuration(mins);
    // Recalculate end from start + new duration
    if (startAt) setEndAt(addMinutesToDatetimeLocal(startAt, mins));
  };

  const handleEndChange = (value) => {
    setEndAt(value);
    // Only recalculate duration when end is valid and after start
    if (!value || !startAt) return;
    const start = new Date(startAt);
    const end = new Date(value);
    if (isNaN(end.getTime()) || end <= start) return;
    const mins = Math.round((end - start) / 60000);
    if (mins >= 5) setDuration(mins);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!startAt) return;
    const isoWithTz = appendLocalTimezone(startAt);
    onSave({ start_at: isoWithTz, duration, area_id: areaId || null, notes });
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      {/* Scrim */}
      <div
        onClick={onClose}
        style={{
          position: 'absolute',
          inset: 0,
          background: overlay.scrim,
          animation: 'fadeIn 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        }}
      />

      {/* Panel */}
      <form
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="block-modal-title"
        onSubmit={handleSubmit}
        style={{
          position: 'relative',
          width: '380px',
          maxWidth: '90vw',
          maxHeight: '85vh',
          overflowY: 'auto',
          background: color.s2,
          borderRadius: radius.lg,
          boxShadow: elevation[3],
          padding: space['2xl'],
          display: 'flex',
          flexDirection: 'column',
          gap: space.lg,
          animation: 'scaleInFlex 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 id="block-modal-title" style={{
            fontFamily: font.sans,
            fontSize: '15px',
            fontWeight: 700,
            color: color.text,
            margin: 0,
          }}>
            {isNew ? 'Nuevo bloque' : 'Editar bloque'}
          </h3>
          <button
            type="button"
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              color: color.muted,
              cursor: 'pointer',
              padding: space.xs,
            }}
          >
            <X size="18" />
          </button>
        </div>

        {/* Start time */}
        <label style={{ display: 'flex', flexDirection: 'column', gap: space.xs }}>
          <span style={labelStyle}>Hora inicio</span>
          <input
            type="datetime-local"
            value={startAt}
            onChange={(e) => handleStartChange(e.target.value)}
            required
          />
        </label>

        {/* Duration + End time — bidirectional */}
        <div style={{ display: 'flex', gap: space.md }}>
          <label style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: space.xs }}>
            <span style={labelStyle}>Duración (min)</span>
            <input
              type="number"
              min={5}
              step={5}
              value={duration}
              onChange={(e) => handleDurationChange(e.target.value)}
            />
          </label>
          <label style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: space.xs }}>
            <span style={labelStyle}>Hora fin</span>
            <input
              type="datetime-local"
              value={endAt}
              onChange={(e) => handleEndChange(e.target.value)}
            />
          </label>
        </div>

        {/* Area — optional */}
        <label style={{ display: 'flex', flexDirection: 'column', gap: space.xs }}>
          <span style={labelStyle}>Área</span>
          <select value={areaId} onChange={(e) => setAreaId(e.target.value)}>
            <option value="">Sin área</option>
            {(areas ?? []).map(a => (
              <option key={a.id} value={a.id}>{a.name}</option>
            ))}
          </select>
        </label>

        {/* Notes */}
        <label style={{ display: 'flex', flexDirection: 'column', gap: space.xs }}>
          <span style={labelStyle}>Notas</span>
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={2}
            style={{ resize: 'vertical' }}
          />
        </label>

        {/* Actions */}
        <div style={{ display: 'flex', gap: space.sm, justifyContent: 'flex-end', paddingTop: space.sm }}>
          {!isNew && onDelete && (
            <button
              type="button"
              onClick={onDelete}
              style={{
                padding: `${space.sm} ${space.md}`,
                background: 'rgba(239,68,68,0.12)',
                color: '#EF4444',
                border: 'none',
                borderRadius: radius.md,
                fontFamily: font.sans,
                fontSize: '13px',
                fontWeight: 600,
                cursor: 'pointer',
                marginRight: 'auto',
                transition: `background ${motion.fast}`,
              }}
            >
              Eliminar
            </button>
          )}
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: `${space.sm} ${space.lg}`,
              background: color.s3,
              color: color.text,
              border: 'none',
              borderRadius: radius.md,
              fontFamily: font.sans,
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: `background ${motion.fast}`,
            }}
          >
            Cancelar
          </button>
          <button
            type="submit"
            style={{
              padding: `${space.sm} ${space.lg}`,
              background: color.yellow,
              color: '#000',
              border: 'none',
              borderRadius: radius.md,
              fontFamily: font.sans,
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: `background ${motion.fast}`,
            }}
          >
            {isNew ? 'Crear' : 'Guardar'}
          </button>
        </div>
      </form>
    </div>
  );
}

const labelStyle = {
  fontFamily: font.mono,
  fontSize: '11px',
  color: color.muted2,
  textTransform: 'uppercase',
  letterSpacing: '0.08em',
};

/**
 * Appends the local timezone offset to a datetime-local value.
 * "2026-04-12T16:00" → "2026-04-12T16:00:00+02:00"
 */
function appendLocalTimezone(dtLocal) {
  if (!dtLocal) return dtLocal;
  if (dtLocal.includes('+') || dtLocal.includes('Z')) return dtLocal;
  const d = new Date(dtLocal);
  const offset = -d.getTimezoneOffset();
  const sign = offset >= 0 ? '+' : '-';
  const hh = String(Math.floor(Math.abs(offset) / 60)).padStart(2, '0');
  const mm = String(Math.abs(offset) % 60).padStart(2, '0');
  const base = dtLocal.length === 16 ? dtLocal + ':00' : dtLocal;
  return `${base}${sign}${hh}:${mm}`;
}
