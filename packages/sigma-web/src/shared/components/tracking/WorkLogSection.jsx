import { useState } from 'react';
import { color, font, motion, radius, space } from '../../tokens';
import { useAddWorkLog } from '../../../entities/tracking/hooks/useAddWorkLog';

// ─── Helpers ─────────────────────────────────────────────────────────────────

function formatMinutes(n) {
  if (n < 60) return `${n} min`;
  const h = Math.floor(n / 60);
  const m = n % 60;
  return m === 0 ? `${h}h` : `${h}h ${m}min`;
}

function formatRelative(dateStr) {
  if (!dateStr) return '';
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 86400000);
  if (diff === 0) return 'hoy';
  if (diff === 1) return 'ayer';
  return `hace ${diff} días`;
}

function totalMinutes(workLog) {
  return (workLog ?? []).reduce((acc, e) => acc + (e.minutes ?? 0), 0);
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function WorkLogSection({ cardId, spaceId, workLog }) {
  const [desc,  setDesc]  = useState('');
  const [time,  setTime]  = useState(25);
  const [unit,  setUnit]  = useState('min'); // 'min' | 'h'

  const { mutate: addEntry, isPending } = useAddWorkLog(cardId, spaceId);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!desc.trim() || time <= 0) return;
    const minutes = unit === 'h' ? time * 60 : time;
    addEntry({ description: desc.trim(), minutes }, {
      onSuccess: () => { setDesc(''); setTime(25); setUnit('min'); },
    });
  };

  const sorted  = [...(workLog ?? [])].reverse();
  const total   = totalMinutes(workLog);
  const canSubmit = desc.trim().length > 0 && time > 0;

  return (
    <div style={{ marginBottom: '18px' }}>
      {/* Section label */}
      <p style={sectionLabelStyle}>Vitácora de trabajo</p>

      {/* Form */}
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '14px' }}>
        <div>
          <label style={fieldLabelStyle} htmlFor="wl-desc">Trabajo realizado</label>
          <input
            id="wl-desc"
            type="text"
            value={desc}
            onChange={e => setDesc(e.target.value)}
            placeholder="Describe el trabajo"
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Time input */}
          <div>
            <label style={fieldLabelStyle} htmlFor="wl-time">Tiempo</label>
            <input
              id="wl-time"
              type="number"
              value={time}
              min={1}
              onChange={e => setTime(Number(e.target.value))}
              style={{ width: '70px', textAlign: 'center' }}
            />
          </div>

          {/* Unit toggle */}
          <div
            role="group"
            aria-label="Unidad de tiempo"
            style={{ display: 'flex', gap: '2px', alignSelf: 'flex-end', marginBottom: '1px' }}
          >
            {['min', 'h'].map(u => (
              <button
                key={u}
                type="button"
                aria-pressed={unit === u}
                onClick={() => setUnit(u)}
                style={{
                  padding:      '4px 10px',
                  borderRadius: radius.sm,
                  fontSize:     '11px',
                  fontWeight:   600,
                  fontFamily:   font.sans,
                  border:       unit === u ? 'none' : `1px solid ${color.border}`,
                  background:   unit === u ? color.yellow : 'transparent',
                  color:        unit === u ? '#000' : color.muted,
                  cursor:       'pointer',
                  transition:   `all ${motion.fast}`,
                }}
              >
                {u}
              </button>
            ))}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={!canSubmit || isPending}
            style={{
              alignSelf:    'flex-end',
              background:   color.s3,
              border:       `1px solid ${canSubmit ? color.yellow : color.border2}`,
              color:        canSubmit ? color.yellow : color.muted,
              borderRadius: '8px',
              padding:      '7px 14px',
              fontSize:     '11px',
              fontFamily:   font.mono,
              cursor:       canSubmit ? 'pointer' : 'not-allowed',
              transition:   `all ${motion.fast}`,
              whiteSpace:   'nowrap',
              opacity:      isPending ? 0.55 : 1,
            }}
          >
            + Registrar
          </button>
        </div>
      </form>

      {/* List */}
      {sorted.length > 0 && (
        <>
          <ul role="list" style={{ listStyle: 'none', margin: 0, padding: 0 }}>
            {sorted.map((entry, i) => (
              <li
                key={entry.id ?? `${entry.logged_at}-${i}`}
                role="listitem"
                style={{
                  display:      'flex',
                  justifyContent: 'space-between',
                  alignItems:   'flex-start',
                  padding:      '8px 0',
                  borderBottom: i < sorted.length - 1 ? `1px solid ${color.border}` : 'none',
                  gap:          '12px',
                }}
              >
                <span style={{
                  fontSize:          '12px',
                  color:             color.text,
                  fontFamily:        font.sans,
                  display:           '-webkit-box',
                  WebkitLineClamp:   2,
                  WebkitBoxOrient:   'vertical',
                  overflow:          'hidden',
                  flex:              1,
                }}>
                  {entry.log}
                </span>
                <div style={{ flexShrink: 0, textAlign: 'right' }}>
                  <p style={{ margin: 0, fontSize: '11px', color: color.muted, fontFamily: font.mono }}>
                    {formatMinutes(entry.minutes)}
                  </p>
                  <p style={{ margin: '1px 0 0', fontSize: '10px', color: color.muted2, fontFamily: font.sans }}>
                    {formatRelative(entry.logged_at)}
                  </p>
                </div>
              </li>
            ))}
          </ul>

          {/* Total */}
          {total > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', paddingTop: '10px', borderTop: `1px solid ${color.border}` }}>
              <span style={{ fontSize: '10px', color: color.muted2, fontFamily: font.sans }}>Total:</span>
              <span style={{ fontSize: '12px', color: color.text, fontFamily: font.mono, fontWeight: 700 }}>
                {formatMinutes(total)}
              </span>
            </div>
          )}
        </>
      )}
    </div>
  );
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const sectionLabelStyle = {
  margin: '0 0 10px',
  fontSize: '9px',
  color: color.muted,
  fontFamily: font.mono,
  letterSpacing: '0.1em',
  textTransform: 'uppercase',
  fontWeight: 700,
};

const fieldLabelStyle = {
  display: 'block',
  marginBottom: '4px',
  fontSize: '9px',
  color: color.muted,
  fontFamily: font.mono,
  letterSpacing: '0.08em',
  textTransform: 'uppercase',
  fontWeight: 700,
};
