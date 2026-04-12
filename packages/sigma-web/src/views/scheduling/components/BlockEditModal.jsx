import { useState } from 'react';
import { color, font, radius, space, elevation, motion, overlay } from '../../../shared/tokens';
import { X } from '../../../shared/components/Icons';

export default function BlockEditModal({ block, areas, onSave, onDelete, onClose }) {
  const isNew = !block?.id;
  const [startAt, setStartAt] = useState(block?.start_at ?? '');
  const [duration, setDuration] = useState(block?.duration ?? 60);
  const [areaId, setAreaId] = useState(block?.area_id ?? '');
  const [notes, setNotes] = useState(block?.notes ?? '');

  const handleSubmit = (e) => {
    e.preventDefault();
    // datetime-local gives "2026-04-12T16:00" without TZ — append local offset
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
        onSubmit={handleSubmit}
        style={{
          position: 'relative',
          width: '380px',
          maxWidth: '90vw',
          background: color.s2,
          borderRadius: radius.lg,
          boxShadow: elevation[3],
          padding: space['2xl'],
          display: 'flex',
          flexDirection: 'column',
          gap: space.lg,
          animation: 'scaleIn 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{
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
          <span style={{ fontFamily: font.mono, fontSize: '11px', color: color.muted2, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Hora inicio
          </span>
          <input
            type="datetime-local"
            value={startAt}
            onChange={(e) => setStartAt(e.target.value)}
            required
          />
        </label>

        {/* Duration */}
        <label style={{ display: 'flex', flexDirection: 'column', gap: space.xs }}>
          <span style={{ fontFamily: font.mono, fontSize: '11px', color: color.muted2, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Duracion (minutos)
          </span>
          <input
            type="number"
            min={15}
            step={15}
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
            required
          />
        </label>

        {/* Area */}
        <label style={{ display: 'flex', flexDirection: 'column', gap: space.xs }}>
          <span style={{ fontFamily: font.mono, fontSize: '11px', color: color.muted2, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Area
          </span>
          <select value={areaId} onChange={(e) => setAreaId(e.target.value)}>
            <option value="">Sin area</option>
            {(areas ?? []).map(a => (
              <option key={a.id} value={a.id}>{a.name}</option>
            ))}
          </select>
        </label>

        {/* Notes */}
        <label style={{ display: 'flex', flexDirection: 'column', gap: space.xs }}>
          <span style={{ fontFamily: font.mono, fontSize: '11px', color: color.muted2, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            Notas
          </span>
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

/**
 * Appends the local timezone offset to a datetime-local value.
 * "2026-04-12T16:00" → "2026-04-12T16:00:00+02:00"
 */
function appendLocalTimezone(dtLocal) {
  if (!dtLocal) return dtLocal;
  if (dtLocal.includes('+') || dtLocal.includes('Z')) return dtLocal; // already has TZ
  const d = new Date(dtLocal);
  const offset = -d.getTimezoneOffset();
  const sign = offset >= 0 ? '+' : '-';
  const hh = String(Math.floor(Math.abs(offset) / 60)).padStart(2, '0');
  const mm = String(Math.abs(offset) % 60).padStart(2, '0');
  // Ensure seconds are present for ISO compliance
  const base = dtLocal.length === 16 ? dtLocal + ':00' : dtLocal;
  return `${base}${sign}${hh}:${mm}`;
}
