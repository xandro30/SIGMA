import { useState, useRef, useEffect } from 'react';
import { color, font, radius, space, elevation, motion, slideOver } from '../../../shared/tokens';
import { X } from '../../../shared/components/Icons';
import { useEscapeKey } from '../../../shared/hooks/useEscapeKey';
import DayTemplateList from './DayTemplateList';
import WeekTemplateList from './WeekTemplateList';

const TABS = [
  { id: 'day', label: 'Plantillas de dia' },
  { id: 'week', label: 'Plantillas de semana' },
];

export default function TemplatePanel({ spaceId, areas, weekStart, onClose, onApplied }) {
  useEscapeKey(onClose);
  const [activeTab, setActiveTab] = useState('day');
  const panelRef = useRef(null);
  useEffect(() => {
    const panel = panelRef.current;
    if (!panel) return;
    const focusable = panel.querySelectorAll('button, input, select, textarea, [tabindex]:not([tabindex="-1"])');
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
    panel.addEventListener('keydown', trap);
    return () => panel.removeEventListener('keydown', trap);
  }, [activeTab]);

  return (
    <>
      {/* Scrim */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0, zIndex: slideOver.zIndex - 1,
          background: slideOver.scrim,
          animation: 'fadeIn 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        }}
      />

      {/* Panel */}
      <div ref={panelRef} role="dialog" aria-modal="true" aria-label="Panel de plantillas" style={{
        position: 'fixed', top: '56px', right: 0, bottom: 0,
        width: slideOver.width, maxWidth: '100vw',
        background: slideOver.background,
        borderLeft: slideOver.borderLeft,
        zIndex: slideOver.zIndex,
        display: 'flex', flexDirection: 'column',
        boxShadow: elevation[3],
        animation: 'slideInFromRight 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
      }}>
        {/* Header */}
        <div style={{
          padding: `${space.lg} ${space.xl}`,
          borderBottom: `1px solid ${color.border}`,
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          flexShrink: 0,
        }}>
          <h3 style={{
            fontFamily: font.sans, fontSize: '15px', fontWeight: 700,
            color: color.text, margin: 0,
          }}>
            Plantillas
          </h3>
          <button
            type="button" onClick={onClose}
            aria-label="Cerrar panel de plantillas"
            style={{ background: 'none', border: 'none', color: color.muted, cursor: 'pointer', padding: space.xs }}
          >
            <X size="18" />
          </button>
        </div>

        {/* Tabs */}
        <div role="tablist" style={{
          display: 'flex', gap: '2px', padding: `${space.sm} ${space.xl}`,
          borderBottom: `1px solid ${color.border}`,
          flexShrink: 0,
        }}>
          {TABS.map(tab => (
            <button
              key={tab.id}
              role="tab"
              aria-selected={activeTab === tab.id}
              id={`tab-${tab.id}`}
              aria-controls={`tabpanel-${tab.id}`}
              onClick={() => setActiveTab(tab.id)}
              style={{
                flex: 1, padding: `${space.sm} ${space.md}`,
                background: activeTab === tab.id ? color.s3 : 'transparent',
                border: 'none', borderRadius: radius.md,
                fontFamily: font.sans, fontSize: '12px', fontWeight: 600,
                color: activeTab === tab.id ? color.text : color.muted,
                cursor: 'pointer',
                transition: `all ${motion.fast}`,
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <div role="tabpanel" id={`tabpanel-${activeTab}`} aria-labelledby={`tab-${activeTab}`} style={{ flex: 1, overflow: 'auto' }}>
          {activeTab === 'day' && (
            <DayTemplateList spaceId={spaceId} areas={areas} onApplied={onApplied} />
          )}
          {activeTab === 'week' && (
            <WeekTemplateList spaceId={spaceId} weekStart={weekStart} onApplied={onApplied} />
          )}
        </div>
      </div>
    </>
  );
}
