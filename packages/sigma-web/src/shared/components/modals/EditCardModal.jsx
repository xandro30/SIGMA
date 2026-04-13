import { useState } from 'react';
import { color, font, priority as pt, getAreaHex } from '../../tokens';
import { useEscapeKey } from '../../hooks/useEscapeKey';
import { useUIStore } from '../../store/useUIStore';
import { useSpaces } from '../../../entities/space/hooks/useSpaces';
import { useAreas } from '../../../entities/area/hooks/useAreas';
import { useProjects } from '../../../entities/project/hooks/useProjects';
import { useEpicsByArea } from '../../../entities/epic/hooks/useEpics';
import { useUpdateCard, useMoveCard, usePromoteCard, useDemoteCard } from '../../../entities/card/hooks/useCards';

const TRIAGE_STAGES = [
  { id: 'inbox',      label: 'Inbox',      color: '#999999' },
  { id: 'refinement', label: 'Refinement', color: '#F5C518' },
  { id: 'backlog',    label: 'Backlog',    color: '#8B5CF6' },
];

const F = { background: color.s2, border: `1.5px solid ${color.border2}`, borderRadius: '8px', color: '#fff', fontSize: '13px', padding: '9px 13px', fontFamily: font.sans, width: '100%', outline: 'none' };

// Sección plegable
function Section({ label, accent, children, defaultOpen = true }) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div style={{ border: `1px solid ${color.border}`, borderRadius: '10px', overflow: 'hidden', flexShrink: 0 }}>
      <button onClick={() => setOpen(o => !o)} style={{ width: '100%', background: color.s2, border: 'none', padding: '10px 14px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}>
        <span style={{ fontSize: '11px', color: accent ?? '#fff', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>{label}</span>
        <span style={{ color: '#888', fontSize: '12px' }}>{open ? '▲' : '▼'}</span>
      </button>
      {open && <div style={{ padding: '14px', background: color.s1, display: 'flex', flexDirection: 'column', gap: '12px' }}>{children}</div>}
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div>
      <p style={{ margin: '0 0 6px', fontSize: '10px', color: '#fff', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>{label}</p>
      {children}
    </div>
  );
}

export default function EditCardModal({ card, onClose }) {
  useEscapeKey(onClose);
  const activeSpaceId = useUIStore(s => s.activeSpaceId);
  const { data: spaces   = [] } = useSpaces();
  const { data: areas    = [] } = useAreas();

  const { mutate: updateCard, isPending: saving } = useUpdateCard(activeSpaceId);
  const { mutate: moveCard    } = useMoveCard(activeSpaceId);
  const { mutate: promoteCard } = usePromoteCard(activeSpaceId);
  const { mutate: demoteCard  } = useDemoteCard(activeSpaceId);

  const space = spaces.find(s => s.id === activeSpaceId);
  const allStates = space?.workflow_states ?? [];

  // Estado local del formulario
  const [title,       setTitle]       = useState(card.title ?? '');
  const [description, setDescription] = useState(card.description ?? '');
  const [priority,    setPriority]    = useState(card.priority ?? 'medium');
  const [areaId,      setAreaId]      = useState(card.area_id ?? '');
  const [epicId,      setEpicId]      = useState(card.epic_id ?? '');
  const [labelsRaw,   setLabelsRaw]   = useState((card.labels ?? []).join(', '));

  const { data: epics    = [] } = useEpicsByArea(areaId);
  const { data: projects = [] } = useProjects(areaId);

  // Agrupar épicas por proyecto para el <optgroup>
  const epicsByProject = projects
    .map(p => ({ project: p, epics: epics.filter(e => e.project_id === p.id) }))
    .filter(g => g.epics.length > 0);
  const projectIds   = new Set(projects.map(p => p.id));
  const orphanEpics  = epics.filter(e => !projectIds.has(e.project_id));

  // Estado actual de la card
  const isInTriage   = !!card.pre_workflow_stage;
  const isInWorkflow = !!card.workflow_state_id;
  const currentStage = isInTriage
    ? TRIAGE_STAGES.find(s => s.id === card.pre_workflow_stage)
    : null;
  const currentState = isInWorkflow
    ? allStates.find(s => s.id === card.workflow_state_id)
    : null;
  const accentColor = isInTriage ? (currentStage?.color ?? '#888') : color.yellow;

  const handleSave = () => {
    if (!title.trim()) return;
    updateCard({
      id: card.id,
      title:       title.trim(),
      description: description.trim() || null,
      priority,
      area_id:     areaId  || null,
      epic_id:     epicId  || null,
      labels:      labelsRaw.split(',').map(s => s.trim()).filter(Boolean),
    }, { onSuccess: onClose });
  };

  const handleMoveToTriageStage = (stage) => {
    // Si está en workflow → demote a triage
    // Si está en triage → mover entre stages (usando demote)
    demoteCard({ cardId: card.id, stage }, { onSuccess: onClose });
  };

  const handleMoveToWorkflow = (stateId) => {
    if (isInTriage) {
      promoteCard({ cardId: card.id, targetStateId: stateId }, { onSuccess: onClose });
    } else {
      moveCard({ cardId: card.id, targetStateId: stateId }, { onSuccess: onClose });
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div onClick={onClose} style={{ position: 'fixed', inset: 0, background: '#00000095', zIndex: 600, backdropFilter: 'blur(4px)' }} />

      {/* Modal */}
      <div style={{
        position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%,-50%)',
        width: '560px', maxWidth: '96vw', maxHeight: '90vh',
        background: color.s1,
        borderTop: `4px solid ${accentColor}`,
        borderRight: `1px solid ${color.border}`,
        borderBottom: `1px solid ${color.border}`,
        borderLeft: `1px solid ${color.border}`,
        borderRadius: '14px', zIndex: 601,
        display: 'flex', flexDirection: 'column',
        boxShadow: '0 40px 100px #000000ee', overflow: 'hidden',
      }}>

        {/* Header */}
        <div style={{ padding: '14px 18px', borderBottom: `1px solid ${color.border}`, background: `rgba(255,255,255,0.02)`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '14px', fontWeight: 800, color: '#fff', fontFamily: font.sans }}>Editar card</span>
            {/* Badge de stage actual */}
            <span style={{ fontSize: '11px', fontWeight: 800, color: accentColor, background: `${accentColor}20`, border: `1px solid ${accentColor}50`, padding: '2px 10px', borderRadius: '5px', fontFamily: font.mono }}>
              {isInTriage ? currentStage?.label.toUpperCase() : currentState?.name ?? '—'}
            </span>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: '18px' }}>✕</button>
        </div>

        {/* Body scrollable */}
        <div style={{ overflowY: 'auto', flex: 1, minHeight: 0, padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>

          {/* ── Sección 1: Contenido ── */}
          <Section label="Contenido" defaultOpen={true}>
            <Field label="Título *">
              <input autoFocus value={title} onChange={e => setTitle(e.target.value)} style={F} />
            </Field>
            <Field label="Descripción">
              <textarea value={description} onChange={e => setDescription(e.target.value)} rows={3} style={{ ...F, resize: 'vertical' }} />
            </Field>
            <Field label="Labels (separadas por coma)">
              <input value={labelsRaw} onChange={e => setLabelsRaw(e.target.value)} placeholder="bug, backend, urgente" style={F} />
            </Field>
          </Section>

          {/* ── Sección 2: Prioridad ── */}
          <Section label="Prioridad" defaultOpen={true}>
            <div style={{ display: 'flex', gap: '8px' }}>
              {Object.entries(pt).map(([k, p]) => (
                <button key={k} onClick={() => setPriority(k)} style={{
                  flex: 1, padding: '9px 0', borderRadius: '8px',
                  border: `2px solid ${priority === k ? p.color : color.border2}`,
                  background: priority === k ? p.bg : 'transparent',
                  color: priority === k ? p.color : '#aaa',
                  cursor: 'pointer', fontSize: '11px', fontWeight: 800, fontFamily: font.mono,
                }}>{p.label}</button>
              ))}
            </div>
          </Section>

          {/* ── Sección 3: Asignación ── */}
          <Section label="Asignación" defaultOpen={true}>
            <Field label="Área">
              <select value={areaId} onChange={e => { setAreaId(e.target.value); setEpicId(''); }} style={{ ...F, cursor: 'pointer' }}>
                <option value="">Sin área</option>
                {areas.map(a => {
                  const hex = getAreaHex(a.color_id);
                  return <option key={a.id} value={a.id}>{a.name}</option>;
                })}
              </select>
            </Field>
            <Field label="Épica">
              <select
                value={epicId}
                onChange={e => setEpicId(e.target.value)}
                disabled={!areaId}
                style={{ ...F, cursor: areaId ? 'pointer' : 'not-allowed', opacity: areaId ? 1 : 0.5 }}
              >
                <option value="">{!areaId ? 'Selecciona un área primero' : 'Sin épica'}</option>
                {epicsByProject.map(({ project, epics: pEpics }) => (
                  <optgroup key={project.id} label={project.name}>
                    {pEpics.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
                  </optgroup>
                ))}
                {orphanEpics.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
              </select>
            </Field>
          </Section>

          {/* ── Sección 4: Movimiento de stage ── */}
          <Section label="Mover stage" accent={accentColor} defaultOpen={true}>

            {/* Triage stages */}
            <div>
              <p style={{ margin: '0 0 8px', fontSize: '10px', color: '#fff', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                {isInWorkflow ? '↩ Volver a Triage' : 'Mover en Triage'}
              </p>
              <div style={{ display: 'flex', gap: '6px' }}>
                {TRIAGE_STAGES.filter(s => s.id !== 'inbox' || isInTriage).map(s => {
                  // Desde workflow nunca se puede volver a Inbox
                  if (isInWorkflow && s.id === 'inbox') return null;
                  // Resaltar stage actual
                  const isCurrent = isInTriage && card.pre_workflow_stage === s.id;
                  return (
                    <button key={s.id} onClick={() => !isCurrent && handleMoveToTriageStage(s.id)} style={{
                      flex: 1, padding: '9px 0', borderRadius: '8px',
                      border: `2px solid ${isCurrent ? s.color : color.border2}`,
                      background: isCurrent ? `${s.color}25` : 'transparent',
                      color: isCurrent ? s.color : '#ccc',
                      cursor: isCurrent ? 'default' : 'pointer',
                      fontSize: '12px', fontWeight: 800, fontFamily: font.mono,
                      opacity: isCurrent ? 1 : 0.8,
                    }}>
                      {isCurrent ? '✓ ' : ''}{s.label}
                    </button>
                  );
                }).filter(Boolean)}
              </div>
            </div>

            {/* Workflow states */}
            <div>
              <p style={{ margin: '0 0 8px', fontSize: '10px', color: '#fff', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>→ Mover al Workflow</p>
              <select
                value={isInWorkflow ? card.workflow_state_id : ''}
                onChange={e => { if (e.target.value) handleMoveToWorkflow(e.target.value); }}
                style={{ ...F, cursor: allStates.length > 0 ? 'pointer' : 'not-allowed', opacity: allStates.length > 0 ? 1 : 0.5 }}
              >
                {!isInWorkflow && <option value="" disabled>Seleccionar estado...</option>}
                {allStates.map(s => (
                  <option key={s.id} value={s.id}>
                    {s.name}{isInWorkflow && card.workflow_state_id === s.id ? ' (actual)' : ''}
                  </option>
                ))}
              </select>
            </div>
          </Section>

        </div>

        {/* Footer */}
        <div style={{ padding: '12px 18px', borderTop: `1px solid ${color.border}`, background: `rgba(255,255,255,0.02)`, display: 'flex', justifyContent: 'flex-end', gap: '8px', flexShrink: 0 }}>
          <button onClick={onClose} style={{ background: 'transparent', border: `1px solid ${color.border2}`, color: '#fff', borderRadius: '8px', padding: '8px 18px', cursor: 'pointer', fontSize: '13px', fontFamily: font.mono, fontWeight: 700 }}>Cancelar</button>
          <button onClick={handleSave} disabled={!title.trim() || saving} style={{
            background: title.trim() ? color.yellow : color.s3, border: 'none',
            color: title.trim() ? '#000' : '#888', borderRadius: '8px',
            padding: '8px 24px', cursor: title.trim() ? 'pointer' : 'not-allowed',
            fontSize: '13px', fontWeight: 800, fontFamily: font.sans,
            opacity: saving ? 0.6 : 1,
          }}>
            {saving ? 'Guardando…' : 'Guardar cambios'}
          </button>
        </div>
      </div>
    </>
  );
}
