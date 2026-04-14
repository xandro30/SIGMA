import { useState, useRef } from 'react';
import { color, font, elevation, motion, radius, overlay } from '../../tokens';
import { useFocusTrap } from '../../hooks/useFocusTrap';

export default function StopSessionModal({ card, minutesWorked, onSave, onDiscard, onClose }) {
  const modalRef = useRef(null);
  useFocusTrap(modalRef, onClose);

  const title    = card?.title ?? '';
  const subtitle = title.length > 50 ? title.slice(0, 50) + '…' : title;
  const minLabel = `${minutesWorked ?? 0} min trabajados`;

  return (
    <>
      <div
        aria-hidden="true"
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0,
          background: 'rgba(0,0,0,0.45)',
          zIndex: 500,
          animation: 'fadeIn 120ms ease forwards',
        }}
      />

      <div
        ref={modalRef}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="stop-session-title"
        aria-describedby="stop-session-desc"
        tabIndex={-1}
        style={{
          position:     'fixed',
          top:          '50%',
          left:         '50%',
          width:        '320px',
          maxWidth:     '94vw',
          background:   color.s1,
          border:       `1px solid ${color.border2}`,
          borderRadius: radius.md,
          zIndex:       501,
          boxShadow:    elevation[3],
          padding:      '18px',
          animation:    'scaleIn 180ms cubic-bezier(0.16,1,0.3,1) forwards',
        }}
      >
        {/* Header */}
        <p id="stop-session-title" style={{ margin: '0 0 2px', fontSize: '14px', fontWeight: 600, color: color.text, fontFamily: font.sans }}>
          Detener sesión
        </p>
        <p id="stop-session-desc" style={{ margin: '0 0 14px', fontSize: '11px', color: color.muted, fontFamily: font.sans }}>
          {subtitle} · {minLabel}
        </p>

        <div style={{ borderTop: `1px solid ${color.border}`, marginBottom: '14px' }} />

        {/* Save option */}
        <OptionCard
          icon="💾"
          iconBg="rgba(245,197,24,0.10)"
          iconBorder="rgba(245,197,24,0.20)"
          title="Guardar trabajo"
          description={`Se registran ${minutesWorked ?? 0} min en la vitácora de la card`}
          titleColor={color.text}
          onClick={onSave}
          autoFocus
        />

        {/* Discard option */}
        <OptionCard
          icon="🗑"
          iconBg="rgba(220,60,60,0.08)"
          iconBorder="rgba(220,60,60,0.18)"
          title="Descartar sesión"
          description="Se borra la sesión activa sin registrar tiempo"
          titleColor="#c06060"
          onClick={onDiscard}
        />

        {/* Cancel */}
        <div style={{ textAlign: 'center', marginTop: '4px' }}>
          <button
            onClick={onClose}
            style={{ background: 'none', border: 'none', fontSize: '11px', color: color.muted2, cursor: 'pointer', fontFamily: font.sans }}
          >
            Cancelar — seguir trabajando
          </button>
        </div>
      </div>
    </>
  );
}

function OptionCard({ icon, iconBg, iconBorder, title, description, titleColor, onClick, autoFocus }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      autoFocus={autoFocus}
      style={{
        width:        '100%',
        background:   hov ? color.s3 : color.s4,
        border:       `1px solid ${hov ? color.border2 : color.border}`,
        borderRadius: '7px',
        padding:      '11px 13px',
        marginBottom: '8px',
        cursor:       'pointer',
        display:      'flex',
        alignItems:   'center',
        gap:          '10px',
        textAlign:    'left',
        transition:   `all ${motion.fast}`,
      }}
    >
      <div style={{
        width: '28px', height: '28px', flexShrink: 0,
        borderRadius: '6px',
        background: iconBg,
        border: `1px solid ${iconBorder}`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '13px',
      }}>
        {icon}
      </div>
      <div>
        <p style={{ margin: 0, fontSize: '12px', color: titleColor, fontWeight: 600, fontFamily: font.sans }}>
          {title}
        </p>
        <p style={{ margin: '1px 0 0', fontSize: '10px', color: color.muted, fontFamily: font.sans }}>
          {description}
        </p>
      </div>
    </button>
  );
}
