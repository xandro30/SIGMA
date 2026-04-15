import { useState, useEffect, useRef } from 'react';
import { color, font, elevation, motion, radius } from '../../tokens';

export const fieldStyle = {
  width:        '100%',
  background:   color.s2,
  border:       `1.5px solid ${color.border2}`,
  borderRadius: radius.md,
  color:        color.text,
  fontSize:     '13px',
  padding:      '9px 12px',
  fontFamily:   font.sans,
  boxSizing:    'border-box',
  outline:      'none',
  fontWeight:   500,
  transition:   `border-color ${motion.fast}, box-shadow ${motion.fast}`,
};

export function Field({ label, children }) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <p style={{ margin: '0 0 6px', fontSize: '9px', color: color.muted, fontFamily: font.mono, letterSpacing: '0.1em', fontWeight: 700, textTransform: 'uppercase' }}>
        {label}
      </p>
      {children}
    </div>
  );
}

const FOCUSABLE = 'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';

export default function BaseEditModal({ title, accent, onClose, onSave, saving, children }) {
  const top      = accent ?? color.yellow;
  const modalRef = useRef(null);

  useEffect(() => {
    const prev = document.activeElement;
    modalRef.current?.focus();
    const handleKey = (e) => {
      if (e.key === 'Escape') { onClose(); return; }
      if (e.key === 'Tab') {
        const focusable = Array.from(modalRef.current?.querySelectorAll(FOCUSABLE) ?? []);
        if (!focusable.length) return;
        const first = focusable[0];
        const last  = focusable[focusable.length - 1];
        if (e.shiftKey) {
          if (document.activeElement === first) { e.preventDefault(); last.focus(); }
        } else {
          if (document.activeElement === last)  { e.preventDefault(); first.focus(); }
        }
      }
    };
    document.addEventListener('keydown', handleKey);
    return () => { document.removeEventListener('keydown', handleKey); prev?.focus(); };
  }, [onClose]);

  return (
    <>
      {/* Overlay */}
      <div
        style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)', zIndex: 500, backdropFilter: 'blur(8px)', WebkitBackdropFilter: 'blur(8px)', animation: 'fadeIn 150ms ease forwards' }}
        onClick={onClose}
      />

      {/* Modal */}
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        tabIndex={-1}
        style={{
        position:      'fixed',
        top:           '50%',
        left:          '50%',
        width:         '500px',
        maxWidth:      '94vw',
        maxHeight:     '85vh',
        background:    color.s1,
        border:        `1px solid ${color.border2}`,
        borderTop:     `3px solid ${top}`,
        borderRadius:  radius.lg,
        zIndex:        501,
        display:       'flex',
        flexDirection: 'column',
        boxShadow:     elevation[4],
        overflow:      'hidden',
        animation:     `scaleIn 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards`,
      }}>

        {/* Header */}
        <div style={{
          padding:        '15px 20px',
          borderBottom:   `1px solid ${color.border}`,
          display:        'flex',
          justifyContent: 'space-between',
          alignItems:     'center',
          background:     'rgba(255,255,255,0.02)',
          flexShrink:     0,
        }}>
          <span id="modal-title" style={{ fontSize: '13px', fontWeight: 700, color: color.text, fontFamily: font.sans }}>
            {title}
          </span>
          <CloseButton onClick={onClose} />
        </div>

        {/* Body */}
        <div style={{ padding: '20px', overflowY: 'auto', flex: 1 }}>
          {children}
        </div>

        {/* Footer */}
        <div style={{
          padding:        '13px 20px',
          borderTop:      `1px solid ${color.border}`,
          display:        'flex',
          justifyContent: 'flex-end',
          gap:            '8px',
          background:     'rgba(255,255,255,0.02)',
          flexShrink:     0,
        }}>
          <CancelButton onClick={onClose} />
          <SaveButton accent={top} saving={saving} onClick={onSave} />
        </div>
      </div>
    </>
  );
}

function CloseButton({ onClick }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      aria-label="Cerrar"
      style={{ background: 'none', border: 'none', color: hov ? color.text : color.muted, cursor: 'pointer', fontSize: '18px', lineHeight: 1, padding: '2px 6px', borderRadius: radius.sm, transition: `color ${motion.fast}` }}
    >
      ✕
    </button>
  );
}

function CancelButton({ onClick }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{ background: hov ? color.s3 : 'transparent', border: `1px solid ${color.border2}`, color: color.muted, borderRadius: '8px', padding: '7px 18px', cursor: 'pointer', fontSize: '11px', fontFamily: font.mono, transition: `all ${motion.fast}` }}
    >
      Cancelar
    </button>
  );
}

function SaveButton({ accent, saving, onClick }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      disabled={saving}
      style={{
        background:   accent,
        border:       'none',
        color:        '#111',
        borderRadius: '8px',
        padding:      '7px 22px',
        cursor:       saving ? 'not-allowed' : 'pointer',
        fontSize:     '11px',
        fontFamily:   font.mono,
        fontWeight:   800,
        opacity:      saving ? 0.55 : 1,
        boxShadow:    hov && !saving ? `0 0 14px ${accent}50` : 'none',
        transform:    hov && !saving ? 'translateY(-1px)' : 'none',
        transition:   `all ${motion.fast}`,
      }}
    >
      {saving ? 'Guardando…' : 'Guardar'}
    </button>
  );
}
