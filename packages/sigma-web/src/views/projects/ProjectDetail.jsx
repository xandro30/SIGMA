import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { color, font, getAreaHex } from '../../shared/tokens';
import { useAreas } from '../../entities/area/hooks/useAreas';
import { useProject, useCreateProject } from '../../entities/project/hooks/useProjects';
import { useEpicsBySpace, useCreateEpic } from '../../entities/epic/hooks/useEpics';
import { useCards } from '../../entities/card/hooks/useCards';
import { useUIStore } from '../../shared/store/useUIStore';
import EditProjectModal from '../../shared/components/modals/EditProjectModal';
import EditEpicModal from '../../shared/components/modals/EditEpicModal';
import SummaryBlock from '../../shared/components/SummaryBlock';
import { seededRandom, WS, mockCardCounts } from '../../shared/workStates';
import { FINISH_ID } from '../../shared/tokens';

const TABS = [
  { id:'overview',  label:'Overview'    },
  { id:'active',    label:'En curso'    },
  { id:'planned',   label:'Planificado' },
  { id:'progress',  label:'Progreso'    },
];

const STATUS_COLOR = { active:'#10B981', on_hold:'#F97316', completed:'#6366F1' };
const STATUS_LABEL = { active:'Activo', on_hold:'En pausa', completed:'Completado' };

function EpicRow({ epic, allCards, areaId, projectId, navigate, onEdit }) {
  const epicCards = allCards.filter(c => c.epic_id === epic.id);
  const total  = epicCards.length;
  const done   = epicCards.filter(c => c.workflow_state_id === FINISH_ID).length;
  const active = epicCards.filter(c => c.workflow_state_id && c.workflow_state_id !== FINISH_ID).length;
  const pct    = total > 0 ? Math.round((done/total)*100) : seededRandom(epic.id+'r');
  return (
    <div style={{ display:'flex', alignItems:'center', gap:'10px', padding:'12px 14px', background:color.s2, border:`1px solid ${color.border}`, borderRadius:'9px' }}>
      <div style={{ flex:1, minWidth:0, cursor:'pointer' }} onClick={() => navigate(`/areas/${areaId}/projects/${projectId}/epics/${epic.id}`)}>
        <span style={{ fontSize:'14px', color:'#fff', fontFamily:font.sans, fontWeight:700 }}>{epic.name}</span>
        {epic.description && <p style={{ margin:'3px 0 0', fontSize:'11px', color:'#ccc', fontFamily:font.sans, fontWeight:600 }}>{epic.description}</p>}
      </div>
      <div style={{ display:'flex', gap:'6px', flexShrink:0 }}>
        {[{ ws:WS.active, v:active }, { ws:WS.done, v:done }, { ws:WS.total, v:total }].map(({ ws, v }) => (
          <div key={ws.label} style={{ background:ws.bg, border:`1px solid ${ws.color}50`, borderRadius:'6px', padding:'4px 8px', textAlign:'center' }}>
            <span style={{ fontSize:'13px', color:ws.color, fontFamily:font.mono, fontWeight:800 }}>{v}</span>
          </div>
        ))}
      </div>
      <div style={{ width:'60px', flexShrink:0 }}>
        <div style={{ display:'flex', justifyContent:'flex-end', marginBottom:'4px' }}>
          <span style={{ fontSize:'11px', color:'#fff', fontFamily:font.mono, fontWeight:800 }}>{pct}%</span>
        </div>
        <div style={{ height:'4px', background:color.border2, borderRadius:'2px' }}>
          <div style={{ height:'100%', width:`${pct}%`, background:'#10B981', borderRadius:'2px' }} />
        </div>
      </div>
      <button onClick={onEdit} style={{ background:'none', border:`1px solid ${color.border2}`, borderRadius:'6px', color:'#fff', cursor:'pointer', padding:'5px 9px', fontSize:'12px', fontFamily:font.mono, fontWeight:700, flexShrink:0 }}>✏</button>
      <button onClick={() => navigate(`/areas/${areaId}/projects/${projectId}/epics/${epic.id}`)} style={{ background:'none', border:'none', color:'#aaa', fontSize:'18px', cursor:'pointer', flexShrink:0 }}>›</button>
    </div>
  );
}

function TabOverview({ project, epics, allCards, areaId, projectId, navigate, onEditProject, onEditEpic, hex }) {
  const activeSpaceId = useUIStore(s => s.activeSpaceId);
  const { mutate: createEpic, isPending } = useCreateEpic(activeSpaceId);
  const [newName, setNewName] = useState('');

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'20px' }}>
      {/* Info proyecto */}
      <div style={{ background:color.s1, border:`1px solid ${color.border}`, borderLeft:`4px solid ${hex}`, borderRadius:'12px', padding:'18px 20px' }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'flex-start', marginBottom:'12px' }}>
          <div style={{ flex:1 }}>
            {project?.description
              ? <p style={{ margin:0, fontSize:'13px', color:'#fff', fontFamily:font.sans, fontWeight:600, lineHeight:'1.6' }}>{project.description}</p>
              : <p style={{ margin:0, fontSize:'13px', color:'#888', fontFamily:font.sans, fontWeight:600 }}>Sin descripción</p>
            }
          </div>
          <button onClick={onEditProject} style={{ background:'none', border:`1px solid ${color.border2}`, borderRadius:'7px', color:'#fff', cursor:'pointer', padding:'6px 12px', fontSize:'12px', fontFamily:font.mono, fontWeight:700, flexShrink:0, marginLeft:'12px' }}>✏ Editar</button>
        </div>
        {project?.objectives?.length > 0 && (
          <div>
            <p style={{ margin:'0 0 10px', fontSize:'10px', color:'#fff', fontFamily:font.mono, fontWeight:700, letterSpacing:'0.1em', textTransform:'uppercase' }}>Objetivos</p>
            {project.objectives.map((obj, i) => {
              const pct = seededRandom(project.id + obj + i);
              return (
                <div key={i} style={{ marginBottom:'10px' }}>
                  <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'4px' }}>
                    <span style={{ fontSize:'13px', color:'#fff', fontFamily:font.sans, fontWeight:700 }}>▸ {obj}</span>
                    <span style={{ fontSize:'12px', color:hex, fontFamily:font.mono, fontWeight:800 }}>{pct}%</span>
                  </div>
                  <div style={{ height:'5px', background:color.border2, borderRadius:'3px' }}>
                    <div style={{ height:'100%', width:`${pct}%`, background:hex, borderRadius:'3px' }} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Lista épicas */}
      <div>
        <p style={{ margin:'0 0 12px', fontSize:'11px', color:'#fff', fontFamily:font.mono, fontWeight:700, letterSpacing:'0.12em', textTransform:'uppercase' }}>Épicas ({epics.length})</p>
        <div style={{ display:'flex', flexDirection:'column', gap:'6px', marginBottom:'12px' }}>
          {epics.map(e => <EpicRow key={e.id} epic={e} allCards={allCards} areaId={areaId} projectId={projectId} navigate={navigate} onEdit={() => onEditEpic(e)} />)}
          {epics.length === 0 && <p style={{ fontSize:'13px', color:'#888', fontFamily:font.sans, fontWeight:600 }}>Sin épicas. Crea la primera abajo.</p>}
        </div>
        <div style={{ display:'flex', gap:'8px' }}>
          <input value={newName} onChange={e => setNewName(e.target.value)} onKeyDown={e => e.key==='Enter' && newName.trim() && createEpic({ name:newName.trim(), project_id:projectId }, { onSuccess:() => setNewName('') })} placeholder="Nombre de la épica…" />
          <button onClick={() => newName.trim() && createEpic({ name:newName.trim(), project_id:projectId }, { onSuccess:() => setNewName('') })} disabled={!newName.trim()||isPending} style={{ background:newName.trim()?hex:color.s3, border:'none', color:newName.trim()?'#000':'#888', borderRadius:'8px', padding:'9px 18px', fontSize:'13px', fontWeight:800, fontFamily:font.sans, cursor:newName.trim()?'pointer':'default' }}>+ Épica</button>
        </div>
      </div>
    </div>
  );
}

function TabActive({ epics, allCards, areaId, projectId, hex }) {
  const navigate = useNavigate();
  const activeEpics = epics.filter(e => allCards.some(c => c.epic_id === e.id && c.workflow_state_id && c.workflow_state_id !== FINISH_ID));
  if (!activeEpics.length) return <div style={{ padding:'40px', textAlign:'center' }}><p style={{ fontSize:'14px', color:'#fff', fontFamily:font.sans, fontWeight:700 }}>Sin épicas con trabajo en curso</p></div>;
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'14px' }}>
      {activeEpics.map(e => <SummaryBlock key={e.id} type="epic" data={e} epics={[]} hex={hex} navigateTo={`/areas/${areaId}/projects/${projectId}/epics/${e.id}`} />)}
    </div>
  );
}

function TabPlanned({ epics, allCards, areaId, projectId, hex, navigate }) {
  const planned = epics.filter(e => !allCards.some(c => c.epic_id === e.id && c.workflow_state_id));
  if (!planned.length) return <div style={{ padding:'40px', textAlign:'center' }}><p style={{ fontSize:'14px', color:'#fff', fontFamily:font.sans, fontWeight:700 }}>Todas las épicas tienen trabajo en curso</p></div>;
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'10px' }}>
      {planned.map(e => {
        const counts = mockCardCounts(e.id);
        return (
          <div key={e.id} onClick={() => navigate(`/areas/${areaId}/projects/${projectId}/epics/${e.id}`)} style={{ display:'flex', alignItems:'center', gap:'12px', padding:'14px 16px', background:color.s1, border:`1px solid ${color.border}`, borderRadius:'10px', cursor:'pointer' }}>
            <div style={{ width:'8px', height:'8px', borderRadius:'50%', background:hex, flexShrink:0 }} />
            <div style={{ flex:1 }}>
              <span style={{ fontSize:'14px', color:'#fff', fontFamily:font.sans, fontWeight:700 }}>{e.name}</span>
              {e.description && <p style={{ margin:'3px 0 0', fontSize:'11px', color:'#ccc', fontFamily:font.sans, fontWeight:600 }}>{e.description}</p>}
            </div>
            <div style={{ display:'flex', gap:'6px' }}>
              {[{ ws:WS.total, v:counts.total }].map(({ ws, v }) => (
                <div key={ws.label} style={{ background:ws.bg, border:`1px solid ${ws.color}50`, borderRadius:'6px', padding:'4px 10px' }}>
                  <span style={{ fontSize:'13px', color:ws.color, fontFamily:font.mono, fontWeight:800 }}>{v} cards</span>
                </div>
              ))}
            </div>
            <span style={{ color:'#aaa', fontSize:'18px' }}>›</span>
          </div>
        );
      })}
    </div>
  );
}

function TabProgress({ epics, allCards, hex }) {
  const total = epics.length;
  const done  = epics.filter(e => {
    const ec = allCards.filter(c => c.epic_id === e.id);
    return ec.length > 0 && ec.every(c => c.workflow_state_id === FINISH_ID);
  }).length;
  const pct = total > 0 ? Math.round((done/total)*100) : 0;

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:'20px' }}>
      {/* Macro */}
      <div style={{ background:color.s1, border:`1px solid ${color.border}`, borderRadius:'12px', padding:'20px' }}>
        <p style={{ margin:'0 0 12px', fontSize:'10px', color:'#fff', fontFamily:font.mono, fontWeight:700, letterSpacing:'0.12em', textTransform:'uppercase' }}>Progreso del proyecto</p>
        <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'8px' }}>
          <span style={{ fontSize:'13px', color:'#fff', fontFamily:font.sans, fontWeight:700 }}>{done}/{total} épicas completadas</span>
          <span style={{ fontSize:'20px', color:WS.done.color, fontFamily:font.mono, fontWeight:800 }}>{pct}%</span>
        </div>
        <div style={{ height:'10px', background:color.border2, borderRadius:'5px', overflow:'hidden' }}>
          <div style={{ height:'100%', width:`${pct}%`, background:`linear-gradient(90deg, ${WS.active.color}, ${WS.done.color})`, borderRadius:'5px' }} />
        </div>
      </div>

      {/* Por épica */}
      <div style={{ background:color.s1, border:`1px solid ${color.border}`, borderRadius:'12px', padding:'20px' }}>
        <p style={{ margin:'0 0 14px', fontSize:'10px', color:'#fff', fontFamily:font.mono, fontWeight:700, letterSpacing:'0.12em', textTransform:'uppercase' }}>Por épica</p>
        <div style={{ display:'flex', flexDirection:'column', gap:'12px' }}>
          {epics.map(e => {
            const ec  = allCards.filter(c => c.epic_id === e.id);
            const ep  = ec.length > 0 ? Math.round((ec.filter(c => c.workflow_state_id===FINISH_ID).length / ec.length)*100) : seededRandom(e.id+'p');
            return (
              <div key={e.id}>
                <div style={{ display:'flex', justifyContent:'space-between', marginBottom:'5px' }}>
                  <span style={{ fontSize:'13px', color:'#fff', fontFamily:font.sans, fontWeight:700 }}>{e.name}</span>
                  <span style={{ fontSize:'12px', color:hex, fontFamily:font.mono, fontWeight:800 }}>{ep}%</span>
                </div>
                <div style={{ height:'6px', background:color.border2, borderRadius:'3px' }}>
                  <div style={{ height:'100%', width:`${ep}%`, background:hex, borderRadius:'3px' }} />
                </div>
              </div>
            );
          })}
          {epics.length === 0 && <p style={{ fontSize:'13px', color:'#888', fontFamily:font.sans, fontWeight:600 }}>Sin épicas</p>}
        </div>
      </div>
    </div>
  );
}

export default function ProjectDetail() {
  const { areaId, projectId } = useParams();
  const navigate      = useNavigate();
  const activeSpaceId = useUIStore(s => s.activeSpaceId);

  const { data: areas    = [] } = useAreas();
  const { data: project }       = useProject(projectId);
  const { data: allEpics = [] } = useEpicsBySpace(activeSpaceId);
  const { data: cards    = [] } = useCards(activeSpaceId);

  const area   = areas.find(a => a.id === areaId);
  const hex    = getAreaHex(area?.color_id);
  const epics  = allEpics.filter(e => e.project_id === projectId);

  const [tab,         setTab]         = useState('overview');
  const [editProject, setEditProject] = useState(false);
  const [editEpic,    setEditEpic]    = useState(null);

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden' }}>
      {/* Header */}
      <div style={{ padding:'18px 24px', borderBottom:`1px solid ${color.border}`, flexShrink:0, background:`rgba(255,255,255,0.02)` }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center' }}>
          <div style={{ display:'flex', alignItems:'center', gap:'12px' }}>
            <div style={{ width:'4px', height:'38px', background:hex, borderRadius:'2px' }} />
            <div>
              <h1 style={{ margin:0, fontSize:'20px', fontWeight:800, color:'#fff', fontFamily:font.sans }}>{project?.name ?? '…'}</h1>
              {project?.status && <span style={{ fontSize:'11px', color:STATUS_COLOR[project.status], background:`${STATUS_COLOR[project.status]}20`, border:`1px solid ${STATUS_COLOR[project.status]}50`, padding:'2px 9px', borderRadius:'4px', fontFamily:font.mono, fontWeight:700 }}>{STATUS_LABEL[project.status]}</span>}
            </div>
          </div>
          <div style={{ display:'flex', gap:'8px' }}>
            <span style={{ fontSize:'12px', color:'#aaa', fontFamily:font.mono, fontWeight:700, alignSelf:'center' }}>{epics.length} épicas</span>
          </div>
        </div>
        {/* Tabs */}
        <div style={{ display:'flex', gap:'4px', marginTop:'14px' }}>
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)} style={{ padding:'7px 18px', borderRadius:'8px', border:'none', background:tab===t.id?hex:'transparent', color:tab===t.id?'#000':'#fff', fontSize:'13px', fontWeight:800, fontFamily:font.sans, cursor:'pointer', transition:'all 0.15s' }}>{t.label}</button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div style={{ flex:1, overflowY:'auto', padding:'20px 24px' }}>
        {tab === 'overview'  && <TabOverview  project={project} epics={epics} allCards={cards} areaId={areaId} projectId={projectId} navigate={navigate} onEditProject={() => setEditProject(true)} onEditEpic={setEditEpic} hex={hex} />}
        {tab === 'active'    && <TabActive    epics={epics} allCards={cards} areaId={areaId} projectId={projectId} hex={hex} />}
        {tab === 'planned'   && <TabPlanned   epics={epics} allCards={cards} areaId={areaId} projectId={projectId} hex={hex} navigate={navigate} />}
        {tab === 'progress'  && <TabProgress  epics={epics} allCards={cards} hex={hex} />}
      </div>

      {editProject && project && <EditProjectModal project={project} areaId={areaId} onClose={() => setEditProject(false)} />}
      {editEpic    &&            <EditEpicModal    epic={editEpic}   areaId={areaId} onClose={() => setEditEpic(null)} />}
    </div>
  );
}
// PATCH: asegurar project_id en createEpic — aplicado en TabOverview via props
