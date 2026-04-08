import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { color, font } from '../../shared/tokens';
import { useSpaces, useCreateSpace } from '../../entities/space/hooks/useSpaces';
import { spacesApi } from '../../api/spaces';
import { useQueryClient } from '@tanstack/react-query';
import PageHeader from '../../shared/components/PageHeader';
import SectionLabel from '../../shared/components/SectionLabel';

const BEGIN_ID  = '00000000-0000-4000-a000-000000000001';
const FINISH_ID = '00000000-0000-4000-a000-000000000002';

function Btn({ onClick, children, variant = 'default' }) {
  const v = { default: { bg: 'transparent', b: color.border2, c: color.muted }, primary: { bg: color.yellow, b: color.yellow, c: '#111' } }[variant] ?? { bg: 'transparent', b: color.border2, c: color.muted };
  return <button onClick={onClick} style={{ background: v.bg, border: `1px solid ${v.b}`, color: v.c, borderRadius: '7px', padding: '6px 14px', cursor: 'pointer', fontSize: '11px', fontFamily: font.mono, fontWeight: 700 }}>{children}</button>;
}

export default function SpaceSettings() {
  const { spaceId } = useParams();
  const navigate    = useNavigate();
  const qc          = useQueryClient();
  const { data: spaces = [] }         = useSpaces();
  const { mutate: createSpace, isPending: creating } = useCreateSpace();

  const space = spaces.find(s => s.id === spaceId);
  const [newStateName,  setNewStateName]  = useState('');
  const [newStateOrder, setNewStateOrder] = useState(1);
  const [newSpaceName,  setNewSpaceName]  = useState('');
  const [fromId, setFromId] = useState('');
  const [toId,   setToId]   = useState('');

  const allStates = space ? [{ id: BEGIN_ID, name: 'BEGIN' }, ...(space.workflow_states ?? []), { id: FINISH_ID, name: 'FINISH' }] : [];

  const inp = { background: color.s2, border: `1.5px solid ${color.border2}`, borderRadius: '8px', color: color.text, fontSize: '12px', padding: '8px 12px', fontFamily: font.sans };

  const addState = async () => {
    if (!newStateName.trim() || !space) return;
    await spacesApi.addWorkflowState(space.id, { name: newStateName.trim(), order: newStateOrder });
    qc.invalidateQueries({ queryKey: ['spaces'] });
    setNewStateName(''); setNewStateOrder(o => o + 1);
  };

  const removeState = async stateId => {
    if (!space) return;
    await spacesApi.removeWorkflowState(space.id, stateId);
    qc.invalidateQueries({ queryKey: ['spaces'] });
  };

  const addTransition = async () => {
    if (!fromId || !toId || !space) return;
    await spacesApi.addTransition(space.id, { from_id: fromId, to_id: toId });
    qc.invalidateQueries({ queryKey: ['spaces'] });
    setFromId(''); setToId('');
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <PageHeader breadcrumbs={[{ label: 'Workspace', href: '/workspace' }, { label: 'Settings' }]} title={space?.name ?? 'Spaces'} subtitle="Configura tu workflow" actions={<Btn onClick={() => navigate('/workspace')}>← Volver</Btn>} />
      <div style={{ flex: 1, overflowY: 'auto', padding: '0 24px 24px', display: 'flex', gap: '24px' }}>
        {space && (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ background: color.s1, border: `1px solid ${color.border}`, borderRadius: '12px', padding: '20px' }}>
              <SectionLabel>Estados del workflow</SectionLabel>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px', marginBottom: '14px' }}>
                {[{ id: BEGIN_ID, name: 'BEGIN', fixed: true, c: color.yellow }, ...(space.workflow_states ?? []).map(s => ({ ...s, fixed: false, c: color.muted })), { id: FINISH_ID, name: 'FINISH', fixed: true, c: '#10B981' }].map(s => (
                  <div key={s.id} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 12px', background: color.s2, border: `1px solid ${color.border}`, borderRadius: '8px' }}>
                    <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: s.c }} />
                    <span style={{ flex: 1, fontSize: '12px', color: s.fixed ? s.c : color.text, fontFamily: s.fixed ? font.mono : font.sans, fontWeight: s.fixed ? 700 : 500 }}>{s.name}</span>
                    {s.fixed && <span style={{ fontSize: '9px', color: color.muted2, fontFamily: font.mono }}>FIJO</span>}
                    {!s.fixed && <button onClick={() => removeState(s.id)} style={{ background: 'none', border: 'none', color: '#EF4444', cursor: 'pointer', fontSize: '12px' }}>✕</button>}
                  </div>
                ))}
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <input value={newStateName} onChange={e => setNewStateName(e.target.value)} onKeyDown={e => e.key === 'Enter' && addState()} placeholder="Nombre del estado…" style={{ ...inp, flex: 1 }} />
                <input value={newStateOrder} onChange={e => setNewStateOrder(Number(e.target.value))} type="number" min={1} style={{ ...inp, width: '60px', textAlign: 'center' }} />
                <Btn onClick={addState} variant="primary">+ Añadir</Btn>
              </div>
            </div>
          </div>
        )}
        <div style={{ width: '260px', flexShrink: 0, display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ background: color.s1, border: `1px solid ${color.border}`, borderRadius: '12px', padding: '18px' }}>
            <SectionLabel>Tus Spaces</SectionLabel>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '14px' }}>
              {spaces.map(s => (
                <button key={s.id} onClick={() => navigate(`/spaces/${s.id}/settings`)} style={{ background: s.id === spaceId ? `${color.yellow}15` : 'transparent', border: `1px solid ${s.id === spaceId ? color.yellow + '50' : color.border}`, color: s.id === spaceId ? color.yellow : color.muted, borderRadius: '7px', padding: '8px 12px', cursor: 'pointer', fontSize: '11px', fontFamily: font.sans, textAlign: 'left', fontWeight: s.id === spaceId ? 700 : 400 }}>{s.name}</button>
              ))}
            </div>
            <SectionLabel>Nuevo Space</SectionLabel>
            <div style={{ display: 'flex', gap: '6px' }}>
              <input value={newSpaceName} onChange={e => setNewSpaceName(e.target.value)} onKeyDown={e => e.key === 'Enter' && !creating && createSpace({ name: newSpaceName.trim() }, { onSuccess: s => { setNewSpaceName(''); navigate(`/spaces/${s.id}/settings`); } })} placeholder="Nombre…" style={{ ...inp, flex: 1 }} />
              <Btn onClick={() => !creating && newSpaceName.trim() && createSpace({ name: newSpaceName.trim() }, { onSuccess: s => { setNewSpaceName(''); navigate(`/spaces/${s.id}/settings`); } })} variant="primary">+</Btn>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
