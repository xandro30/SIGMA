import { useState } from 'react';
import { color, font, motion, radius } from '../../tokens';

export default function SessionCompletedBanner({ minutesLogged, onDismiss }) {
  const [hov, setHov] = useState(false);

  return (
    <div
      role="status"
      aria-live="polite"
      style={{
        display:      'flex',
        alignItems:   'center',
        justifyContent: 'space-between',
        gap:          '8px',
        padding:      '8px 10px',
        margin:       '0 0 8px',
        background:   color.s4,
        border:       `1px solid rgba(16,185,129,0.30)`,
        borderLeft:   `3px solid ${color.green}`,
        borderRadius: radius.sm,
        animation:    'slideInUp 220ms cubic-bezier(0.16,1,0.3,1) forwards',
      }}
    >
      <span style={{ fontSize: '11px', color: color.text, fontFamily: font.sans, fontWeight: 500 }}>
        ✓ Sesión completada · {minutesLogged} min registrados en vitácora
      </span>
      <button
        onClick={onDismiss}
        onMouseEnter={() => setHov(true)}
        onMouseLeave={() => setHov(false)}
        aria-label="Cerrar notificación de sesión completada"
        style={{
          background: 'none',
          border:     'none',
          color:      hov ? color.text : color.muted2,
          cursor:     'pointer',
          fontSize:   '13px',
          lineHeight: 1,
          padding:    '2px 4px',
          flexShrink: 0,
          transition: `color ${motion.fast}`,
        }}
      >
        ✕
      </button>
    </div>
  );
}
