import { useState } from 'react';
import { color, font, priority as pt } from '../../tokens';
import { useUIStore } from '../../store/useUIStore';
import { useAreas } from '../../../entities/area/hooks/useAreas';
import { useEpicsBySpace } from '../../../entities/epic/hooks/useEpics';
import { useCreateCard } from '../../../entities/card/hooks/useCards';

const F = {
  width: '100%',
  background: color.s2,
  border: `1.5px solid ${color.border2}`,
  borderRadius: '8px',
  color: color.text,
  fontSize: '13px',
  padding: '9px 13px',
  fontFamily: font.sans,
  boxSizing: 'border-box',
  outline: 'none',
};

const STAGES = [
  { id: 'inbox',      label: 'Inbox',       desc: 'Captura rápida',     c: '#888888' },
  { id: 'refinement', label: 'Refinement',  desc: 'En análisis',        c: '#F5C518' },
  { id: 'backlog',    label: 'Backlog',      desc: 'Listo para sprint',  c: '#8B5CF6' },
];

export default function CreateCardModal() {
  const close         = useUIStore(s => s.closeCreateCard);
  const activeSpaceId = useUIStore(s => s.activeSpaceId);

  const { data: areas = [] } = useAreas();
  const { data: epics = [] } = useEpicsBySpace(activeSpaceId);
  const { mutate: createCard, isPending } = useCreateCard(activeSpaceId);

  const [title,       setTitle]       = useState('');
  const [description, setDescription] = useState('');
  const [priority,    setPriority]    = useState('medium');
  const [stage,       setStage]       = useState('inbox');
  const [areaId,      setAreaId]      = useState('');
  const [epicId,      setEpicId]      = useState('');

  const canCreate = title.trim().length > 0 && !!activeSpaceId;

  const handleCreate = () => {
    if (!canCreate || isPending) return;
    createCard(
      {
        title:         title.trim(),
        description:   description.trim() || null,
        priority,
        initial_stage: stage,
        area_id:       areaId || null,
        epic_id:       epicId || null,
      },
      { onSuccess: close }
    );
  };

  return (
    <>
      <div onClick={close} style={{ position: 'fixed', inset: 0, background: '#00000095', zIndex: 600, backdropFilter: 'blur(4px)' }} />

      <div style={{
        position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%,-50%)',
        width: '500px', maxWidth: '95vw', maxHeight: '90vh',
        background: color.s1, border: `1px solid ${color.border}`,
        borderTop: `3px solid ${color.yellow}`,
        borderRadius: '14px', zIndex: 601,
        display: 'flex', flexDirection: 'column',
        boxShadow: '0 40px 100px #000000dd', overflow: 'hidden',
      }}>

        {/* Header */}
        <div style={{ padding: '16px 20px', borderBottom: `1px solid ${color.border}`, background: `rgba(255,255,255,0.02)`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
          <span style={{ fontSize: '14px', fontWeight: 700, color: color.text, fontFamily: font.sans }}>Nueva card</span>
          <button onClick={close} style={{ background: 'none', border: 'none', color: color.muted, cursor: 'pointer', fontSize: '18px', lineHeight: 1 }}>✕</button>
        </div>

        {/* Body */}
        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px', overflowY: 'auto', flex: 1 }}>

          {/* Título */}
          <div>
            <p style={{ margin: '0 0 6px', fontSize: '9px', color: color.muted2, fontFamily: font.mono, letterSpacing: '0.1em', fontWeight: 700 }}>TÍTULO *</p>
            <input
              autoFocus
              value={title}
              onChange={e => setTitle(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && !e.shiftKey && handleCreate()}
              placeholder="¿En qué hay que trabajar?"
              style={F}
            />
          </div>

          {/* Descripción */}
          <div>
            <p style={{ margin: '0 0 6px', fontSize: '9px', color: color.muted2, fontFamily: font.mono, letterSpacing: '0.1em', fontWeight: 700 }}>DESCRIPCIÓN</p>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              rows={3}
              placeholder="Contexto adicional…"
              style={{ ...F, resize: 'vertical' }}
            />
          </div>

          {/* Prioridad */}
          <div>
            <p style={{ margin: '0 0 8px', fontSize: '9px', color: color.muted2, fontFamily: font.mono, letterSpacing: '0.1em', fontWeight: 700 }}>PRIORIDAD</p>
            <div style={{ display: 'flex', gap: '6px' }}>
              {Object.entries(pt).map(([k, p]) => (
                <button key={k} onClick={() => setPriority(k)} style={{
                  flex: 1, padding: '8px 0', borderRadius: '8px',
                  border: `1.5px solid ${priority === k ? p.color : color.border2}`,
                  background: priority === k ? p.bg : 'transparent',
                  color: priority === k ? p.color : color.muted,
                  cursor: 'pointer', fontSize: '10px', fontWeight: 800,
                  fontFamily: font.mono, transition: 'all 0.1s',
                }}>{p.label}</button>
              ))}
            </div>
          </div>

          {/* Stage destino */}
          <div>
            <p style={{ margin: '0 0 8px', fontSize: '9px', color: color.muted2, fontFamily: font.mono, letterSpacing: '0.1em', fontWeight: 700 }}>DESTINO EN PRE-WORKFLOW</p>
            <div style={{ display: 'flex', gap: '6px' }}>
              {STAGES.map(s => (
                <button key={s.id} onClick={() => setStage(s.id)} style={{
                  flex: 1, padding: '8px 6px', borderRadius: '8px',
                  border: `1.5px solid ${stage === s.id ? s.c : color.border2}`,
                  background: stage === s.id ? `${s.c}20` : 'transparent',
                  color: stage === s.id ? s.c : color.muted,
                  cursor: 'pointer', fontSize: '10px', fontWeight: stage === s.id ? 800 : 500,
                  fontFamily: font.mono, transition: 'all 0.1s',
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px',
                }}>
                  <span>{s.label}</span>
                  <span style={{ fontSize: '8px', color: stage === s.id ? s.c : color.muted2, fontWeight: 400, fontFamily: font.sans }}>{s.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Área + Épica */}
          <div style={{ display: 'flex', gap: '10px' }}>
            <div style={{ flex: 1 }}>
              <p style={{ margin: '0 0 6px', fontSize: '9px', color: color.muted2, fontFamily: font.mono, letterSpacing: '0.1em', fontWeight: 700 }}>ÁREA</p>
              <select value={areaId} onChange={e => { setAreaId(e.target.value); setEpicId(''); }} style={{ ...F, cursor: 'pointer' }}>
                <option value="">Sin área</option>
                {areas.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
              </select>
            </div>
            <div style={{ flex: 1 }}>
              <p style={{ margin: '0 0 6px', fontSize: '9px', color: color.muted2, fontFamily: font.mono, letterSpacing: '0.1em', fontWeight: 700 }}>ÉPICA</p>
              <select value={epicId} onChange={e => setEpicId(e.target.value)} disabled={epics.length === 0} style={{ ...F, cursor: epics.length > 0 ? 'pointer' : 'not-allowed', opacity: epics.length > 0 ? 1 : 0.5 }}>
                <option value="">Sin épica</option>
                {epics.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div style={{ padding: '14px 20px', borderTop: `1px solid ${color.border}`, background: `rgba(255,255,255,0.02)`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
          <span style={{ fontSize: '10px', color: color.muted2, fontFamily: font.mono }}>
            📥 Irá a <strong style={{ color: STAGES.find(s => s.id === stage)?.c }}>{STAGES.find(s => s.id === stage)?.label}</strong>
          </span>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button onClick={close} style={{ background: 'transparent', border: `1px solid ${color.border2}`, color: color.muted, borderRadius: '8px', padding: '8px 18px', cursor: 'pointer', fontSize: '12px', fontFamily: font.mono }}>Cancelar</button>
            <button
              onClick={handleCreate}
              disabled={!canCreate || isPending}
              style={{
                background: canCreate ? color.yellow : color.s3,
                border: 'none', color: canCreate ? '#111' : color.muted2,
                borderRadius: '8px', padding: '8px 24px',
                cursor: canCreate ? 'pointer' : 'not-allowed',
                fontSize: '12px', fontWeight: 800, fontFamily: font.sans,
                opacity: isPending ? 0.6 : 1, transition: 'all 0.15s',
              }}
            >{isPending ? 'Creando…' : 'Crear card'}</button>
          </div>
        </div>
      </div>
    </>
  );
}
