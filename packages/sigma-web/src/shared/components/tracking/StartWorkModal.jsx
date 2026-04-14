import { useState, useRef } from 'react';
import { color, font, elevation, motion, radius, overlay } from '../../tokens';
import { useFocusTrap } from '../../hooks/useFocusTrap';

export default function StartWorkModal({ card, onConfirm, onClose }) {
  const [description, setDescription] = useState('');
  const [workMinutes,  setWorkMinutes]  = useState(25);
  const [breakMinutes, setBreakMinutes] = useState(5);
  const [numRounds,    setNumRounds]    = useState(4);
  const [descError,    setDescError]    = useState(false);

  const modalRef   = useRef(null);
  const textareaRef = useRef(null);
  useFocusTrap(modalRef, onClose);

  // Give focus to textarea after mount (useFocusTrap focuses the modal container first)
  const handleModalFocus = (e) => {
    if (e.target === modalRef.current) textareaRef.current?.focus();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!description.trim()) { setDescError(true); return; }
    onConfirm({
      description: description.trim(),
      work_minutes:  Math.max(1, workMinutes),
      break_minutes: Math.max(0, breakMinutes),
      num_rounds:    Math.max(1, numRounds),
    });
  };

  const cardTitle = card?.title ?? '';
  const subtitle  = cardTitle.length > 60 ? cardTitle.slice(0, 60) + '…' : cardTitle;

  return (
    <>
      {/* Overlay */}
      <div
        aria-hidden="true"
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0,
          background: overlay.scrim,
          backdropFilter: 'blur(8px)',
          WebkitBackdropFilter: 'blur(8px)',
          zIndex: 500,
          animation: 'fadeIn 150ms ease forwards',
        }}
      />

      {/* Modal */}
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="start-work-title"
        tabIndex={-1}
        onFocus={handleModalFocus}
        style={{
          position:      'fixed',
          top:           '50%',
          left:          '50%',
          width:         '420px',
          maxWidth:      '94vw',
          maxHeight:     '85vh',
          background:    color.s1,
          border:        `1px solid ${color.border2}`,
          borderTop:     `3px solid ${color.yellow}`,
          borderRadius:  radius.lg,
          zIndex:        501,
          display:       'flex',
          flexDirection: 'column',
          boxShadow:     elevation[4],
          overflow:      'hidden',
          animation:     'scaleIn 220ms cubic-bezier(0.16,1,0.3,1) forwards',
        }}
      >
        {/* Header */}
        <div style={{
          padding:        '14px 20px',
          borderBottom:   `1px solid ${color.border}`,
          background:     'rgba(255,255,255,0.02)',
          flexShrink:     0,
        }}>
          <p id="start-work-title" style={{ margin: 0, fontSize: '13px', fontWeight: 700, color: color.text, fontFamily: font.sans }}>
            Iniciar sesión de trabajo
          </p>
          {subtitle && (
            <p style={{ margin: '2px 0 0', fontSize: '11px', color: color.muted, fontFamily: font.sans, fontWeight: 400 }}>
              {subtitle}
            </p>
          )}
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} style={{ padding: '20px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '16px' }}>

          {/* Description field */}
          <div>
            <p style={labelStyle}>Trabajo a realizar</p>
            <textarea
              ref={textareaRef}
              value={description}
              onChange={e => { setDescription(e.target.value); if (e.target.value.trim()) setDescError(false); }}
              placeholder="Describe el trabajo de esta sesión…"
              rows={3}
              required
              style={{
                resize:      'vertical',
                borderColor: descError ? '#ef4444' : undefined,
                boxShadow:   descError ? '0 0 0 3px rgba(239,68,68,0.15)' : undefined,
              }}
            />
            {descError && (
              <p style={{ margin: '4px 0 0', fontSize: '10px', color: '#ef4444', fontFamily: font.sans }}>
                Requerido — describe el trabajo a realizar
              </p>
            )}
          </div>

          {/* Timer config row */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '10px' }}>
            <NumField label="Trabajo (min)" value={workMinutes}  onChange={setWorkMinutes}  min={1} />
            <NumField label="Descanso (min)" value={breakMinutes} onChange={setBreakMinutes} min={0} />
            <NumField label="Rondas"         value={numRounds}    onChange={setNumRounds}    min={1} />
          </div>
        </form>

        {/* Footer */}
        <div style={{
          padding:        '12px 20px',
          borderTop:      `1px solid ${color.border}`,
          display:        'flex',
          alignItems:     'center',
          justifyContent: 'space-between',
          background:     'rgba(255,255,255,0.02)',
          flexShrink:     0,
        }}>
          <button
            type="button"
            onClick={onClose}
            style={{ background: 'none', border: 'none', fontSize: '11px', color: color.muted2, cursor: 'pointer', fontFamily: font.sans, padding: '4px 0' }}
          >
            Cancelar
          </button>
          <button
            type="submit"
            form=""
            onClick={handleSubmit}
            disabled={!description.trim()}
            style={{
              background:   !description.trim() ? 'rgba(245,197,24,0.3)' : color.yellow,
              border:       'none',
              color:        '#000',
              fontWeight:   700,
              fontSize:     '11px',
              fontFamily:   font.mono,
              padding:      '7px 22px',
              borderRadius: '8px',
              cursor:       !description.trim() ? 'not-allowed' : 'pointer',
              transition:   `all ${motion.fast}`,
            }}
          >
            ▶ Iniciar sesión
          </button>
        </div>
      </div>
    </>
  );
}

function NumField({ label, value, onChange, min }) {
  return (
    <div>
      <p style={labelStyle}>{label}</p>
      <input
        type="number"
        value={value}
        min={min}
        onChange={e => onChange(Number(e.target.value))}
        style={{ textAlign: 'center' }}
      />
    </div>
  );
}

const labelStyle = {
  margin: '0 0 6px',
  fontSize: '9px',
  color: color.muted2,
  fontFamily: font.mono,
  letterSpacing: '0.1em',
  textTransform: 'uppercase',
  fontWeight: 700,
};
