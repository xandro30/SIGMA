import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { color, font, getAreaHex } from '../../tokens';
import { useAreas } from '../../../entities/area/hooks/useAreas';
import { useProjects } from '../../../entities/project/hooks/useProjects';
import { useEpicsBySpace } from '../../../entities/epic/hooks/useEpics';
import { useUIStore } from '../../store/useUIStore';

const W = '#FFFFFF';

function parseActivePath(pathname) {
  const p = pathname.split('/').filter(Boolean);
  const ai = p.indexOf('areas'), pi = p.indexOf('projects'), ei = p.indexOf('epics');
  return { activeAreaId: ai >= 0 ? p[ai+1] : null, activeProjectId: pi >= 0 ? p[pi+1] : null, activeEpicId: ei >= 0 ? p[ei+1] : null };
}

function EpicList({ projectId, projectHref, activeEpicId }) {
  const nav = useNavigate();
  const activeSpaceId = useUIStore(s => s.activeSpaceId);
  const { data: epics = [] } = useEpicsBySpace(activeSpaceId);
  const list = epics.filter(e => e.project_id === projectId);
  if (!list.length) return <p style={{ padding: '4px 0 4px 32px', fontSize: '12px', color: '#888', fontFamily: font.sans }}>sin épicas</p>;
  return list.map(e => {
    const active = e.id === activeEpicId;
    return (
      <button key={e.id} onClick={() => nav(`${projectHref}/epics/${e.id}`)} style={{
        width: '100%', background: active ? color.yellow : 'transparent',
        border: 'none', borderRadius: '5px',
        padding: '6px 8px 6px 32px', textAlign: 'left',
        display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '2px',
      }}>
        <span style={{ fontSize: '11px', color: active ? '#000' : '#888' }}>◇</span>
        <span style={{ fontSize: '13px', color: active ? '#000' : W, fontFamily: font.sans, fontWeight: 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{e.name}</span>
      </button>
    );
  });
}

function ProjectList({ areaId, areaHref, activeProjectId, activeEpicId }) {
  const nav = useNavigate();
  const { data: projects = [], isLoading } = useProjects(areaId);
  const [exp, setExp] = useState({ [activeProjectId]: true });
  if (isLoading) return <p style={{ padding: '4px 0 4px 18px', fontSize: '12px', color: '#888' }}>cargando…</p>;
  if (!projects.length) return <p style={{ padding: '4px 0 4px 18px', fontSize: '12px', color: '#888', fontFamily: font.sans }}>sin proyectos</p>;
  const STATUS_DOT = { active: '#10B981', on_hold: '#F97316', completed: '#6366F1' };
  return projects.map(p => {
    const active = p.id === activeProjectId;
    const open   = exp[p.id];
    const href   = `${areaHref}/projects/${p.id}`;
    return (
      <div key={p.id}>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <button onClick={() => setExp(s => ({ ...s, [p.id]: !s[p.id] }))} style={{ padding: '5px 4px 5px 12px', color: '#888', background: 'none', border: 'none', fontSize: '11px', flexShrink: 0 }}>
            {open ? '▾' : '▸'}
          </button>
          <button onClick={() => nav(href)} style={{
            flex: 1, background: active ? color.yellow : 'transparent',
            border: 'none', borderRadius: '5px',
            padding: '6px 8px 6px 4px', textAlign: 'left',
            display: 'flex', alignItems: 'center', gap: '7px', minWidth: 0,
          }}>
            <div style={{ width: '7px', height: '7px', borderRadius: '50%', background: active ? '#000' : (STATUS_DOT[p.status] ?? '#888'), flexShrink: 0 }} />
            <span style={{ fontSize: '13px', color: active ? '#000' : W, fontFamily: font.sans, fontWeight: 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{p.name}</span>
          </button>
        </div>
        {open && <EpicList projectId={p.id} projectHref={href} activeEpicId={activeEpicId} />}
      </div>
    );
  });
}

export default function ParaSidebar() {
  const nav = useNavigate();
  const loc = useLocation();
  const { data: areas = [] } = useAreas();
  const { activeAreaId, activeProjectId, activeEpicId } = parseActivePath(loc.pathname);
  const [exp, setExp] = useState({ [activeAreaId]: true });

  return (
    <div style={{ padding: '14px 8px' }}>
      <p style={{ fontSize: '11px', color: W, fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: '10px', paddingLeft: '6px' }}>Áreas</p>
      {areas.map(a => {
        const hex    = getAreaHex(a.color_id);
        const active = a.id === activeAreaId;
        const open   = exp[a.id];
        const href   = `/areas/${a.id}`;
        return (
          <div key={a.id}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <button onClick={() => setExp(s => ({ ...s, [a.id]: !s[a.id] }))} style={{ padding: '5px 4px', color: '#888', background: 'none', border: 'none', fontSize: '11px', flexShrink: 0 }}>
                {open ? '▾' : '▸'}
              </button>
              <button onClick={() => { nav(href); setExp(s => ({ ...s, [a.id]: true })); }} style={{
                flex: 1, background: active ? hex : 'transparent',
                border: 'none', borderRadius: '6px',
                padding: '7px 8px 7px 6px', textAlign: 'left',
                display: 'flex', alignItems: 'center', gap: '8px', minWidth: 0,
              }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: active ? '#000' : hex, flexShrink: 0 }} />
                <span style={{ fontSize: '14px', color: active ? '#000' : W, fontFamily: font.sans, fontWeight: 800, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.name}</span>
              </button>
            </div>
            {open && <ProjectList areaId={a.id} areaHref={href} activeProjectId={activeProjectId} activeEpicId={activeEpicId} />}
          </div>
        );
      })}
    </div>
  );
}
