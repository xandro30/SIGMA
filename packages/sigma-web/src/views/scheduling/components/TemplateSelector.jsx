import { useState } from 'react';
import { color, font, radius, space, elevation, motion, overlay } from '../../../shared/tokens';
import { X, Calendar } from '../../../shared/components/Icons';

export default function TemplateSelector({ templates, onApply, onClose }) {
  const [selected, setSelected] = useState(null);
  const [replace, setReplace] = useState(false);

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      zIndex: 1000,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      <div onClick={onClose} style={{
        position: 'absolute', inset: 0, background: overlay.scrim,
        animation: 'fadeIn 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
      }} />

      <div style={{
        position: 'relative',
        width: '360px',
        maxWidth: '90vw',
        maxHeight: '70vh',
        background: color.s2,
        borderRadius: radius.lg,
        boxShadow: elevation[3],
        padding: space['2xl'],
        display: 'flex',
        flexDirection: 'column',
        gap: space.lg,
        animation: 'scaleIn 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h3 style={{ fontFamily: font.sans, fontSize: '15px', fontWeight: 700, color: color.text, margin: 0 }}>
            Aplicar plantilla
          </h3>
          <button type="button" onClick={onClose} style={{ background: 'none', border: 'none', color: color.muted, cursor: 'pointer', padding: space.xs }}>
            <X size="18" />
          </button>
        </div>

        <div style={{ overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: space.sm }}>
          {(!templates || templates.length === 0) && (
            <p style={{ fontFamily: font.sans, fontSize: '13px', color: color.muted2, textAlign: 'center', padding: space.xl }}>
              No hay plantillas semanales creadas
            </p>
          )}
          {(templates ?? []).map(t => {
            const active = selected === t.id;
            const slotsUsed = Object.values(t.slots).filter(Boolean).length;
            return (
              <button
                key={t.id}
                type="button"
                onClick={() => setSelected(active ? null : t.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: space.md,
                  padding: space.md,
                  background: active ? color.yellowDim : color.s3,
                  border: active ? `1px solid ${color.borderAccent}` : '1px solid transparent',
                  borderRadius: radius.md,
                  cursor: 'pointer',
                  textAlign: 'left',
                  transition: `all ${motion.fast}`,
                }}
              >
                <Calendar size="16" style={{ color: active ? color.yellow : color.muted, flexShrink: 0 }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: font.sans, fontSize: '13px', fontWeight: 600, color: color.text }}>{t.name}</div>
                  <div style={{ fontFamily: font.mono, fontSize: '10px', color: color.muted2 }}>{slotsUsed}/7 dias configurados</div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Replace toggle */}
        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: space.sm,
          fontFamily: font.sans,
          fontSize: '12px',
          color: color.muted,
          cursor: 'pointer',
        }}>
          <input
            type="checkbox"
            checked={replace}
            onChange={(e) => setReplace(e.target.checked)}
            style={{ width: '16px', height: '16px', accentColor: color.yellow }}
          />
          Reemplazar bloques existentes
        </label>

        <div style={{ display: 'flex', gap: space.sm, justifyContent: 'flex-end' }}>
          <button type="button" onClick={onClose} style={{
            padding: `${space.sm} ${space.lg}`, background: color.s3, color: color.text,
            border: 'none', borderRadius: radius.md, fontFamily: font.sans, fontSize: '13px', fontWeight: 600, cursor: 'pointer',
          }}>
            Cancelar
          </button>
          <button
            type="button"
            disabled={!selected}
            onClick={() => selected && onApply({ templateId: selected, replaceExisting: replace })}
            style={{
              padding: `${space.sm} ${space.lg}`, background: selected ? color.yellow : color.disabled,
              color: selected ? '#000' : color.muted, border: 'none', borderRadius: radius.md,
              fontFamily: font.sans, fontSize: '13px', fontWeight: 600,
              cursor: selected ? 'pointer' : 'not-allowed',
              opacity: selected ? 1 : 0.38,
            }}
          >
            Aplicar
          </button>
        </div>
      </div>
    </div>
  );
}
