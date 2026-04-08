import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { color, font, getAreaHex } from '../../shared/tokens';
import { useAreas } from '../../entities/area/hooks/useAreas';
import { useProjects, useCreateProject } from '../../entities/project/hooks/useProjects';
import { useEpicsBySpace } from '../../entities/epic/hooks/useEpics';
import { useUIStore } from '../../shared/store/useUIStore';
import EditAreaModal from '../../shared/components/modals/EditAreaModal';
import EditProjectModal from '../../shared/components/modals/EditProjectModal';
import SummaryBlock from '../../shared/components/SummaryBlock';
import { seededRandom, WS } from '../../shared/workStates';

const TABS = [
  { id: 'overview',  label: 'Overview'   },
  { id: 'active',    label: 'En curso'   },
  { id: 'progress',  label: 'Progreso'   },
];

// ── Tab: Overview ─────────────────────────────────────────────────────────────
function TabOverview({ area, projects, onEditArea, onEditProject, navigate, areaId, hex }) {
  const [newName, setNewName] = useState('');
  const { mutate: createProject, isPending } = useCreateProject(areaId);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Descripción + objetivos del área */}
      <div style={{ background: color.s1, border: `1px solid ${color.border}`, borderLeft: `4px solid ${hex}`, borderRadius: '12px', padding: '18px 20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
          <div>
            {area.description
              ? <p style={{ margin: 0, fontSize: '13px', color: '#FFFFFF', fontFamily: font.sans, fontWeight: 600, lineHeight: '1.6' }}>{area.description}</p>
              : <p style={{ margin: 0, fontSize: '13px', color: '#888', fontFamily: font.sans, fontWeight: 600 }}>Sin descripción</p>
            }
          </div>
          <button onClick={onEditArea} style={{ background: 'none', border: `1px solid ${color.border2}`, borderRadius: '7px', color: '#FFFFFF', cursor: 'pointer', padding: '6px 12px', fontSize: '12px', fontFamily: font.mono, fontWeight: 700, flexShrink: 0, marginLeft: '12px' }}>✏ Editar</button>
        </div>

        {area.objectives?.length > 0 && (
          <div>
            <p style={{ margin: '0 0 10px', fontSize: '10px', color: '#FFFFFF', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Objetivos del área</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {area.objectives.map((obj, i) => {
                const pct = seededRandom(area.id + obj + i);
                return (
                  <div key={i}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontSize: '13px', color: '#FFFFFF', fontFamily: font.sans, fontWeight: 700 }}>▸ {obj}</span>
                      <span style={{ fontSize: '12px', color: hex, fontFamily: font.mono, fontWeight: 800 }}>{pct}%</span>
                    </div>
                    <div style={{ height: '5px', background: color.border2, borderRadius: '3px' }}>
                      <div style={{ height: '100%', width: `${pct}%`, background: hex, borderRadius: '3px' }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Lista de proyectos — navegación */}
      <div>
        <p style={{ margin: '0 0 12px', fontSize: '11px', color: '#FFFFFF', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase' }}>Proyectos ({projects.length})</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '12px' }}>
          {projects.map(p => {
            const SC = { active: '#10B981', on_hold: '#F97316', completed: '#6366F1' };
            const sc = SC[p.status] ?? '#888';
            return (
              <div key={p.id} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '12px 14px', background: color.s2, border: `1px solid ${color.border}`, borderRadius: '9px' }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: sc, flexShrink: 0 }} />
                <span onClick={() => navigate(`/areas/${areaId}/projects/${p.id}`)} style={{ flex: 1, fontSize: '14px', color: '#FFFFFF', fontFamily: font.sans, fontWeight: 700, cursor: 'pointer' }}>{p.name}</span>
                <span style={{ fontSize: '10px', color: sc, background: `${sc}20`, border: `1px solid ${sc}50`, padding: '2px 8px', borderRadius: '4px', fontFamily: font.mono, fontWeight: 700 }}>{p.status?.replace('_', ' ')}</span>
                <button onClick={() => onEditProject(p)} style={{ background: 'none', border: `1px solid ${color.border2}`, borderRadius: '5px', color: '#FFFFFF', cursor: 'pointer', padding: '4px 8px', fontSize: '12px', fontFamily: font.mono }}>✏</button>
                <button onClick={() => navigate(`/areas/${areaId}/projects/${p.id}`)} style={{ background: 'none', border: 'none', color: '#888', fontSize: '16px', cursor: 'pointer' }}>›</button>
              </div>
            );
          })}
          {projects.length === 0 && <p style={{ fontSize: '13px', color: '#888', fontFamily: font.sans, fontWeight: 600 }}>Sin proyectos en esta área</p>}
        </div>

        {/* Crear proyecto */}
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            value={newName}
            onChange={e => setNewName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && newName.trim() && createProject({ name: newName.trim() }, { onSuccess: () => setNewName('') })}
            placeholder="Nombre del nuevo proyecto…"
            style={{ flex: 1 }}
          />
          <button
            onClick={() => newName.trim() && createProject({ name: newName.trim() }, { onSuccess: () => setNewName('') })}
            disabled={!newName.trim() || isPending}
            style={{ background: newName.trim() ? hex : color.s3, border: 'none', color: newName.trim() ? '#000' : '#888', borderRadius: '8px', padding: '9px 18px', fontSize: '13px', fontWeight: 800, fontFamily: font.sans }}>
            + Proyecto
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Tab: En curso ─────────────────────────────────────────────────────────────
function TabActive({ projects, epics, areaId, hex, navigate }) {
  const active = projects.filter(p => p.status === 'active');
  if (!active.length) return (
    <div style={{ padding: '40px', textAlign: 'center' }}>
      <p style={{ fontSize: '14px', color: '#FFFFFF', fontFamily: font.sans, fontWeight: 700 }}>Sin proyectos activos en esta área</p>
    </div>
  );
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      {active.map(p => {
        const projectEpics = epics.filter(e => e.project_id === p.id);
        return (
          <SummaryBlock
            key={p.id}
            type="project"
            data={p}
            epics={projectEpics}
            hex={hex}
            navigateTo={`/areas/${areaId}/projects/${p.id}`}
          />
        );
      })}
    </div>
  );
}

// ── Tab: Progreso ─────────────────────────────────────────────────────────────
function TabProgress({ projects, hex }) {
  const total    = projects.length;
  const done     = projects.filter(p => p.status === 'completed').length;
  const active   = projects.filter(p => p.status === 'active').length;
  const onHold   = projects.filter(p => p.status === 'on_hold').length;
  const pct      = total > 0 ? Math.round((done / total) * 100) : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Barra macro */}
      <div style={{ background: color.s1, border: `1px solid ${color.border}`, borderRadius: '12px', padding: '20px' }}>
        <p style={{ margin: '0 0 12px', fontSize: '10px', color: '#FFFFFF', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase' }}>Progreso del área</p>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '13px', color: '#FFFFFF', fontFamily: font.sans, fontWeight: 700 }}>{done}/{total} proyectos completados</span>
          <span style={{ fontSize: '18px', color: WS.done.color, fontFamily: font.mono, fontWeight: 800 }}>{pct}%</span>
        </div>
        <div style={{ height: '10px', background: color.border2, borderRadius: '5px', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${pct}%`, background: `linear-gradient(90deg, ${WS.active.color}, ${WS.done.color})`, borderRadius: '5px' }} />
        </div>
      </div>

      {/* Stats grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '10px' }}>
        {[
          { label: 'Activos',    value: active, ws: WS.active  },
          { label: 'En pausa',   value: onHold, ws: WS.waiting },
          { label: 'Completados',value: done,   ws: WS.done    },
        ].map(({ label, value, ws }) => (
          <div key={label} style={{ background: ws.bg, border: `1px solid ${ws.color}50`, borderRadius: '10px', padding: '16px', textAlign: 'center' }}>
            <div style={{ fontSize: '28px', fontWeight: 800, color: ws.color, fontFamily: font.mono }}>{value}</div>
            <div style={{ fontSize: '11px', fontWeight: 700, color: '#FFFFFF', fontFamily: font.sans, marginTop: '4px' }}>{label}</div>
          </div>
        ))}
      </div>

      {/* Progreso por proyecto */}
      <div style={{ background: color.s1, border: `1px solid ${color.border}`, borderRadius: '12px', padding: '20px' }}>
        <p style={{ margin: '0 0 14px', fontSize: '10px', color: '#FFFFFF', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase' }}>Por proyecto</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {projects.map(p => {
            const pct = seededRandom(p.id + 'progress');
            return (
              <div key={p.id}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                  <span style={{ fontSize: '13px', color: '#FFFFFF', fontFamily: font.sans, fontWeight: 700 }}>{p.name}</span>
                  <span style={{ fontSize: '12px', color: hex, fontFamily: font.mono, fontWeight: 800 }}>{pct}%</span>
                </div>
                <div style={{ height: '6px', background: color.border2, borderRadius: '3px' }}>
                  <div style={{ height: '100%', width: `${pct}%`, background: hex, borderRadius: '3px' }} />
                </div>
              </div>
            );
          })}
          {projects.length === 0 && <p style={{ fontSize: '13px', color: '#888', fontFamily: font.sans, fontWeight: 600 }}>Sin proyectos</p>}
        </div>
      </div>
    </div>
  );
}

// ── AreaDetail principal ──────────────────────────────────────────────────────
export default function AreaDetail() {
  const { areaId }    = useParams();
  const navigate      = useNavigate();
  const activeSpaceId = useUIStore(s => s.activeSpaceId);

  const { data: areas    = [] }            = useAreas();
  const { data: projects = [], isLoading } = useProjects(areaId);
  const { data: epics    = [] }            = useEpicsBySpace(activeSpaceId);

  const area = areas.find(a => a.id === areaId);
  const hex  = getAreaHex(area?.color_id);

  const [tab,         setTab]         = useState('overview');
  const [editArea,    setEditArea]    = useState(false);
  const [editProject, setEditProject] = useState(null);

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

      {/* ── Header ── */}
      <div style={{ padding: '18px 24px', borderBottom: `1px solid ${color.border}`, flexShrink: 0, background: `rgba(255,255,255,0.02)` }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ width: '4px', height: '38px', background: hex, borderRadius: '2px' }} />
            <div>
              <h1 style={{ margin: 0, fontSize: '20px', fontWeight: 800, color: '#FFFFFF', fontFamily: font.sans }}>{area?.name ?? '…'}</h1>
              <p style={{ margin: '2px 0 0', fontSize: '12px', color: '#FFFFFF', fontFamily: font.mono, fontWeight: 600 }}>{projects.length} proyectos · {epics.filter(e => projects.some(p => p.id === e.project_id)).length} épicas</p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '4px', marginTop: '14px' }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} style={{
              padding: '7px 18px', borderRadius: '8px', border: 'none',
              background: tab === t.id ? hex : 'transparent',
              color: tab === t.id ? '#000000' : '#FFFFFF',
              fontSize: '13px', fontWeight: 800, fontFamily: font.sans,
              cursor: 'pointer', transition: 'all 0.15s',
            }}>{t.label}</button>
          ))}
        </div>
      </div>

      {/* ── Content ── */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px' }}>
        {isLoading
          ? <p style={{ color: '#FFFFFF', fontFamily: font.sans, fontWeight: 700 }}>Cargando…</p>
          : tab === 'overview' ? (
            <TabOverview area={area ?? {}} projects={projects} onEditArea={() => setEditArea(true)} onEditProject={setEditProject} navigate={navigate} areaId={areaId} hex={hex} />
          ) : tab === 'active' ? (
            <TabActive projects={projects} epics={epics} areaId={areaId} hex={hex} navigate={navigate} />
          ) : (
            <TabProgress projects={projects} hex={hex} />
          )
        }
      </div>

      {editArea    && area    && <EditAreaModal    area={area}                       onClose={() => setEditArea(false)} />}
      {editProject &&            <EditProjectModal project={editProject} areaId={areaId} onClose={() => setEditProject(null)} />}
    </div>
  );
}
