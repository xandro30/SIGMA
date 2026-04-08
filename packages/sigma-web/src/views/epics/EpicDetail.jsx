import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { color, font, getAreaHex, priority as pt, PRIORITY_ORDER, BEGIN_ID, FINISH_ID } from '../../shared/tokens';
import { useAreas } from '../../entities/area/hooks/useAreas';
import { useEpic } from '../../entities/epic/hooks/useEpics';
import { useCards, useCreateCard, useMoveCard, usePromoteCard, useDemoteCard } from '../../entities/card/hooks/useCards';
import { useSpaces } from '../../entities/space/hooks/useSpaces';
import { useUIStore } from '../../shared/store/useUIStore';
import EditCardModal from '../../shared/components/modals/EditCardModal';
import EditEpicModal from '../../shared/components/modals/EditEpicModal';
import PriorityBadge from '../../shared/components/PriorityBadge';
import { WS } from '../../shared/workStates';
import { seededRandom } from '../../shared/workStates';

const TABS = [
  { id: 'overview', label: 'Overview' },
  { id: 'cards',    label: 'Cards'    },
  { id: 'progress', label: 'Progreso' },
];

const TRIAGE_STAGES = [
  { id: 'inbox',      label: 'Inbox',  color: '#999' },
  { id: 'refinement', label: 'Refine', color: '#F5C518' },
  { id: 'backlog',    label: 'Backlog',color: '#8B5CF6' },
];

// ── Card item con botón de stage rápido ───────────────────────────────────────
function CardItem({ card, areas, stateLabel, stageColor, isSelected, onSelect, onEdit, onStageClick }) {
  const area = areas.find(a => a.id === card.area_id);
  const hex  = getAreaHex(area?.color_id);
  const pr   = pt[card.priority] ?? pt.low;

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '11px 14px', background: isSelected ? color.s3 : color.s2, border: `1px solid ${isSelected ? color.yellow : color.border}`, borderLeft: `4px solid ${pr.color}`, borderRadius: '8px', cursor: 'pointer', transition: 'all 0.1s' }}>
      <div style={{ flex: 1, minWidth: 0 }} onClick={() => onSelect(card)}>
        <p style={{ margin: 0, fontSize: '13px', color: '#fff', fontFamily: font.sans, fontWeight: 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{card.title}</p>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '4px' }}>
          {area && <><div style={{ width: '5px', height: '5px', borderRadius: '50%', background: hex }} /><span style={{ fontSize: '11px', color: '#ccc', fontFamily: font.mono, fontWeight: 700 }}>{area.name}</span></>}
        </div>
      </div>

      {/* Stage badge — clickable para mover */}
      <button onClick={() => onStageClick(card)} title="Cambiar stage" style={{
        background: `${stageColor}20`, border: `1px solid ${stageColor}60`,
        color: stageColor, borderRadius: '6px', padding: '3px 9px',
        cursor: 'pointer', fontSize: '10px', fontFamily: font.mono, fontWeight: 800,
        flexShrink: 0, letterSpacing: '0.06em',
      }}>
        {stateLabel}
      </button>

      <PriorityBadge value={card.priority} />
      <button onClick={() => onEdit(card)} style={{ background: 'none', border: `1px solid ${color.border2}`, borderRadius: '5px', color: '#fff', cursor: 'pointer', padding: '4px 8px', fontSize: '12px', fontFamily: font.mono, fontWeight: 700, flexShrink: 0 }}>✏</button>
    </div>
  );
}

// ── Mini modal de movimiento rápido de stage ──────────────────────────────────
function StageQuickModal({ card, allStates, onMove, onClose }) {
  const isInTriage   = !!card.pre_workflow_stage;
  const isInWorkflow = !!card.workflow_state_id;
  const TRIAGE = [
    { id: 'refinement', label: 'Refinement', color: '#F5C518' },
    { id: 'backlog',    label: 'Backlog',    color: '#8B5CF6' },
  ];

  return (
    <>
      <div style={{ position: 'fixed', inset: 0, zIndex: 700 }} onClick={onClose} />
      <div style={{ position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', width: '300px', background: color.s1, border: `1px solid ${color.border}`, borderTop: `3px solid ${color.yellow}`, borderRadius: '12px', padding: '16px', zIndex: 701, boxShadow: '0 30px 80px #000' }}>
        <p style={{ margin: '0 0 4px', fontSize: '11px', color: '#fff', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Mover card</p>
        <p style={{ margin: '0 0 12px', fontSize: '12px', color: '#ccc', fontFamily: font.sans, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{card.title}</p>

        {/* Triage stages (nunca Inbox si viene de Workflow) */}
        {!isInWorkflow && (
          <div style={{ marginBottom: '10px' }}>
            <p style={{ margin: '0 0 6px', fontSize: '10px', color: '#888', fontFamily: font.mono, fontWeight: 700, textTransform: 'uppercase' }}>Triage</p>
            <div style={{ display: 'flex', gap: '5px' }}>
              {[{ id: 'inbox', label: 'Inbox', color: '#999' }, ...TRIAGE].map(s => {
                const cur = card.pre_workflow_stage === s.id;
                return (
                  <button key={s.id} onClick={() => !cur && onMove('triage', s.id)} style={{ flex: 1, padding: '7px 0', borderRadius: '7px', border: `1.5px solid ${cur ? s.color : color.border2}`, background: cur ? `${s.color}20` : 'transparent', color: cur ? s.color : '#ccc', cursor: cur ? 'default' : 'pointer', fontSize: '11px', fontFamily: font.mono, fontWeight: 800 }}>
                    {cur ? '✓' : ''} {s.label}
                  </button>
                );
              })}
            </div>
          </div>
        )}
        {isInWorkflow && (
          <div style={{ marginBottom: '10px' }}>
            <p style={{ margin: '0 0 6px', fontSize: '10px', color: '#888', fontFamily: font.mono, fontWeight: 700, textTransform: 'uppercase' }}>↩ Volver a Triage</p>
            <div style={{ display: 'flex', gap: '5px' }}>
              {TRIAGE.map(s => (
                <button key={s.id} onClick={() => onMove('triage', s.id)} style={{ flex: 1, padding: '7px 0', borderRadius: '7px', border: `1.5px solid ${color.border2}`, background: 'transparent', color: '#ccc', cursor: 'pointer', fontSize: '11px', fontFamily: font.mono, fontWeight: 800 }}>{s.label}</button>
              ))}
            </div>
          </div>
        )}

        {/* Workflow */}
        <div>
          <p style={{ margin: '0 0 6px', fontSize: '10px', color: '#888', fontFamily: font.mono, fontWeight: 700, textTransform: 'uppercase' }}>Workflow</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            {allStates.map(s => {
              const cur = card.workflow_state_id === s.id;
              return (
                <button key={s.id} onClick={() => !cur && onMove('workflow', s.id)} style={{ background: cur ? `${color.yellow}20` : color.s2, border: `1px solid ${cur ? color.yellow : color.border2}`, color: cur ? color.yellow : '#fff', borderRadius: '7px', padding: '8px 12px', cursor: cur ? 'default' : 'pointer', fontSize: '12px', fontFamily: font.sans, fontWeight: 700, textAlign: 'left', display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span style={{ color: cur ? color.yellow : '#888' }}>{cur ? '✓' : '→'}</span>
                  <span>{s.name}</span>
                  {cur && <span style={{ fontSize: '10px', color: color.yellow, fontFamily: font.mono }}>(actual)</span>}
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </>
  );
}

// ── Tab Overview ──────────────────────────────────────────────────────────────
function TabOverview({ epic, epicCards, allStates, hex }) {
  const total  = epicCards.length;
  const done   = epicCards.filter(c => c.workflow_state_id === FINISH_ID).length;
  const active = epicCards.filter(c => c.workflow_state_id && c.workflow_state_id !== FINISH_ID).length;
  const wait   = epicCards.filter(c => c.pre_workflow_stage).length;
  const pct    = total > 0 ? Math.round((done / total) * 100) : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ background: color.s1, border: `1px solid ${color.border}`, borderLeft: `4px solid ${hex}`, borderRadius: '12px', padding: '18px 20px' }}>
        {epic?.description
          ? <p style={{ margin: 0, fontSize: '13px', color: '#fff', fontFamily: font.sans, fontWeight: 600, lineHeight: '1.6' }}>{epic.description}</p>
          : <p style={{ margin: 0, fontSize: '13px', color: '#888', fontFamily: font.sans, fontWeight: 600 }}>Sin descripción</p>
        }
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '10px' }}>
        {[{ ws: WS.active, v: active, label: 'En progreso' }, { ws: WS.waiting, v: wait, label: 'En espera' }, { ws: WS.done, v: done, label: 'Completadas' }, { ws: WS.total, v: total, label: 'Total' }].map(({ ws, v, label }) => (
          <div key={label} style={{ background: ws.bg, border: `1.5px solid ${ws.color}50`, borderRadius: '10px', padding: '14px 10px', textAlign: 'center' }}>
            <div style={{ fontSize: '24px', fontWeight: 800, color: ws.color, fontFamily: font.mono }}>{v}</div>
            <div style={{ fontSize: '10px', fontWeight: 700, color: '#fff', fontFamily: font.mono, marginTop: '4px', letterSpacing: '0.06em', textTransform: 'uppercase' }}>{label}</div>
          </div>
        ))}
      </div>
      <div style={{ background: color.s1, border: `1px solid ${color.border}`, borderRadius: '12px', padding: '18px 20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
          <span style={{ fontSize: '13px', color: '#fff', fontFamily: font.sans, fontWeight: 700 }}>Progreso</span>
          <span style={{ fontSize: '18px', color: WS.done.color, fontFamily: font.mono, fontWeight: 800 }}>{pct}%</span>
        </div>
        <div style={{ height: '10px', background: color.border2, borderRadius: '5px', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${pct}%`, background: `linear-gradient(90deg,${WS.active.color},${WS.done.color})`, borderRadius: '5px' }} />
        </div>
      </div>
    </div>
  );
}

// ── Tab Progress ──────────────────────────────────────────────────────────────
function TabProgress({ epicCards, allStates }) {
  const total = epicCards.length;
  const byPriority = ['critical', 'high', 'medium', 'low'].map(k => ({ key: k, pr: pt[k], cnt: epicCards.filter(c => c.priority === k).length }));
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ background: color.s1, border: `1px solid ${color.border}`, borderRadius: '12px', padding: '20px' }}>
        <p style={{ margin: '0 0 14px', fontSize: '10px', color: '#fff', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase' }}>Distribución por estado</p>
        {allStates.map(s => {
          const cnt = epicCards.filter(c => c.workflow_state_id === s.id).length;
          const pct = total > 0 ? Math.round((cnt / total) * 100) : 0;
          const c   = s.id === FINISH_ID ? WS.done.color : s.id === BEGIN_ID ? WS.waiting.color : WS.active.color;
          return (
            <div key={s.id} style={{ marginBottom: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                <span style={{ fontSize: '13px', color: '#fff', fontFamily: font.sans, fontWeight: 700 }}>{s.name}</span>
                <span style={{ fontSize: '12px', color: c, fontFamily: font.mono, fontWeight: 800 }}>{cnt} ({pct}%)</span>
              </div>
              <div style={{ height: '6px', background: color.border2, borderRadius: '3px' }}>
                <div style={{ height: '100%', width: `${pct}%`, background: c, borderRadius: '3px' }} />
              </div>
            </div>
          );
        })}
      </div>
      <div style={{ background: color.s1, border: `1px solid ${color.border}`, borderRadius: '12px', padding: '20px' }}>
        <p style={{ margin: '0 0 14px', fontSize: '10px', color: '#fff', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase' }}>Distribución por prioridad</p>
        <div style={{ display: 'flex', gap: '8px' }}>
          {byPriority.map(({ key, pr, cnt }) => (
            <div key={key} style={{ flex: 1, background: pr.bg, border: `1.5px solid ${pr.color}`, borderRadius: '10px', padding: '12px 8px', textAlign: 'center' }}>
              <div style={{ fontSize: '22px', fontWeight: 800, color: pr.color, fontFamily: font.mono }}>{cnt}</div>
              <div style={{ fontSize: '10px', fontWeight: 800, color: '#fff', fontFamily: font.mono, marginTop: '4px', letterSpacing: '0.06em' }}>{pr.label}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── EpicDetail principal ──────────────────────────────────────────────────────
export default function EpicDetail() {
  const { areaId, projectId, epicId } = useParams();
  const activeSpaceId = useUIStore(s => s.activeSpaceId);

  const { data: areas   = [] } = useAreas();
  const { data: epic }         = useEpic(epicId);
  const { data: spaces  = [] } = useSpaces();
  const { data: allCards= [] } = useCards(activeSpaceId);
  const { mutate: createCard, isPending } = useCreateCard(activeSpaceId);
  const { mutate: moveCard    } = useMoveCard(activeSpaceId);
  const { mutate: promoteCard } = usePromoteCard(activeSpaceId);
  const { mutate: demoteCard  } = useDemoteCard(activeSpaceId);

  const area  = areas.find(a => a.id === areaId);
  const space = spaces.find(s => s.id === activeSpaceId);
  const hex   = getAreaHex(area?.color_id);

  const allStates = space?.workflow_states ?? [];
  const epicCards = allCards.filter(c => c.epic_id === epicId).sort((a, b) => (PRIORITY_ORDER[a.priority] ?? 4) - (PRIORITY_ORDER[b.priority] ?? 4));

  const [tab,          setTab]          = useState('overview');
  const [selectedCard, setSelectedCard] = useState(null);
  const [editCard,     setEditCard]     = useState(null);
  const [editEpic,     setEditEpic]     = useState(false);
  const [stageCard,    setStageCard]    = useState(null);
  const [newTitle,     setNewTitle]     = useState('');
  const [newPriority,  setNewPriority]  = useState('medium');

  // Crear card con contexto completo — area + epic + project ya conocidos
  const handleCreateCard = () => {
    if (!newTitle.trim() || isPending) return;
    createCard({
      title:         newTitle.trim(),
      priority:      newPriority,
      initial_stage: 'inbox',
      area_id:       areaId    || null,  // ← auto-asignado del contexto
      epic_id:       epicId    || null,  // ← auto-asignado del contexto
    }, { onSuccess: () => setNewTitle('') });
  };

  const handleStageMove = (type, id) => {
    if (!stageCard) return;
    if (type === 'triage') {
      demoteCard({ cardId: stageCard.id, stage: id });
    } else {
      if (stageCard.pre_workflow_stage) {
        promoteCard({ cardId: stageCard.id, targetStateId: id });
      } else {
        moveCard({ cardId: stageCard.id, targetStateId: id });
      }
    }
    setStageCard(null);
  };

  const getStateInfo = (card) => {
    if (card.pre_workflow_stage) {
      const s = TRIAGE_STAGES.find(s => s.id === card.pre_workflow_stage) ?? { label: card.pre_workflow_stage, color: '#888' };
      return { label: s.label.toUpperCase(), color: s.color };
    }
    const s = allStates.find(s => s.id === card.workflow_state_id);
    return { label: s?.name ?? '—', color: color.yellow };
  };

  return (
    <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

        {/* Header */}
        <div style={{ padding: '18px 24px', borderBottom: `1px solid ${color.border}`, flexShrink: 0, background: `rgba(255,255,255,0.02)` }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1, minWidth: 0 }}>
              <div style={{ width: '4px', height: '36px', background: hex, borderRadius: '2px', flexShrink: 0 }} />
              <div style={{ minWidth: 0 }}>
                <h1 style={{ margin: 0, fontSize: '18px', fontWeight: 800, color: '#fff', fontFamily: font.sans, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{epic?.name ?? '…'}</h1>
                <p style={{ margin: '2px 0 0', fontSize: '11px', color: '#aaa', fontFamily: font.mono, fontWeight: 700 }}>{epicCards.length} cards en total</p>
              </div>
            </div>
            <button onClick={() => setEditEpic(true)} style={{ background: 'none', border: `1px solid ${color.border2}`, borderRadius: '7px', color: '#fff', cursor: 'pointer', padding: '6px 12px', fontSize: '12px', fontFamily: font.mono, fontWeight: 700, flexShrink: 0, marginLeft: '12px' }}>✏ Editar</button>
          </div>
          <div style={{ display: 'flex', gap: '4px', marginTop: '14px' }}>
            {TABS.map(t => (
              <button key={t.id} onClick={() => setTab(t.id)} style={{ padding: '7px 18px', borderRadius: '8px', border: 'none', background: tab === t.id ? hex : 'transparent', color: tab === t.id ? '#000' : '#fff', fontSize: '13px', fontWeight: 800, fontFamily: font.sans, cursor: 'pointer', transition: 'all 0.15s' }}>{t.label}</button>
            ))}
          </div>
        </div>

        {/* Content */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px' }}>
          {tab === 'overview' && <TabOverview epic={epic} epicCards={epicCards} allStates={allStates} hex={hex} />}
          {tab === 'progress' && <TabProgress epicCards={epicCards} allStates={allStates} />}
          {tab === 'cards' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {/* Crear card — contexto auto-asignado */}
              <div style={{ background: color.s1, border: `1px solid ${color.border}`, borderRadius: '10px', padding: '14px' }}>
                <p style={{ margin: '0 0 10px', fontSize: '10px', color: '#fff', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                  Nueva card — se asignará a esta épica automáticamente
                </p>
                <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                  <input value={newTitle} onChange={e => setNewTitle(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleCreateCard()} placeholder="Título de la card…" />
                  <button onClick={handleCreateCard} disabled={!newTitle.trim() || isPending} style={{ background: newTitle.trim() ? color.yellow : color.s3, border: 'none', color: newTitle.trim() ? '#000' : '#888', borderRadius: '8px', padding: '9px 16px', fontSize: '13px', fontWeight: 800, fontFamily: font.sans, cursor: newTitle.trim() ? 'pointer' : 'default', flexShrink: 0 }}>
                    + Card
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '5px' }}>
                  {Object.entries(pt).map(([k, p]) => (
                    <button key={k} onClick={() => setNewPriority(k)} style={{ flex: 1, padding: '5px 0', borderRadius: '6px', border: `1.5px solid ${newPriority === k ? p.color : color.border2}`, background: newPriority === k ? p.bg : 'transparent', color: newPriority === k ? p.color : '#aaa', cursor: 'pointer', fontSize: '10px', fontWeight: 800, fontFamily: font.mono }}>{p.label}</button>
                  ))}
                </div>
                {/* Contexto visual */}
                <div style={{ display: 'flex', gap: '6px', marginTop: '10px', flexWrap: 'wrap' }}>
                  {area && <span style={{ fontSize: '10px', color: hex, background: `${hex}18`, border: `1px solid ${hex}40`, borderRadius: '4px', padding: '2px 8px', fontFamily: font.mono, fontWeight: 700 }}>📍 {area.name}</span>}
                  {epic && <span style={{ fontSize: '10px', color: '#aaa', background: color.s2, border: `1px solid ${color.border2}`, borderRadius: '4px', padding: '2px 8px', fontFamily: font.mono, fontWeight: 700 }}>◇ {epic.name}</span>}
                  <span style={{ fontSize: '10px', color: '#888', fontFamily: font.mono, fontWeight: 600, alignSelf: 'center' }}>→ irá a Inbox</span>
                </div>
              </div>

              {/* Lista */}
              <p style={{ margin: 0, fontSize: '11px', color: '#fff', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>{epicCards.length} cards · por prioridad · click en stage para mover</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '5px' }}>
                {epicCards.length === 0 && <p style={{ fontSize: '13px', color: '#888', fontFamily: font.sans, fontWeight: 600 }}>Sin cards todavía</p>}
                {epicCards.map(c => {
                  const si = getStateInfo(c);
                  return <CardItem key={c.id} card={c} areas={areas} stateLabel={si.label} stageColor={si.color} isSelected={selectedCard?.id === c.id} onSelect={c => setSelectedCard(prev => prev?.id === c.id ? null : c)} onEdit={setEditCard} onStageClick={setStageCard} />;
                })}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Panel derecho detalle */}
      {selectedCard && tab === 'cards' && (
        <div style={{ width: '280px', flexShrink: 0, borderLeft: `1px solid ${color.border}`, background: '#0d0d0d', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: `1px solid ${color.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '11px', color: '#fff', fontFamily: font.mono, fontWeight: 800, letterSpacing: '0.1em' }}>DETALLE</span>
            <div style={{ display: 'flex', gap: '6px' }}>
              <button onClick={() => setEditCard(selectedCard)} style={{ background: 'none', border: `1px solid ${color.border2}`, borderRadius: '5px', color: color.yellow, cursor: 'pointer', padding: '3px 9px', fontSize: '11px', fontFamily: font.mono, fontWeight: 700 }}>✏ Editar</button>
              <button onClick={() => setSelectedCard(null)} style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: '18px' }}>✕</button>
            </div>
          </div>
          <div style={{ padding: '16px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <PriorityBadge value={selectedCard.priority} size="md" />
              <h3 style={{ margin: '10px 0 0', fontSize: '15px', color: '#fff', fontFamily: font.sans, fontWeight: 800, lineHeight: '1.4' }}>{selectedCard.title}</h3>
            </div>
            {selectedCard.description && <p style={{ margin: 0, fontSize: '12px', color: '#ccc', fontFamily: font.sans, fontWeight: 600, lineHeight: '1.6' }}>{selectedCard.description}</p>}
            <div style={{ padding: '10px 12px', background: color.s2, border: `1px solid ${color.border}`, borderRadius: '8px' }}>
              <p style={{ margin: '0 0 4px', fontSize: '10px', color: '#fff', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Stage actual</p>
              <span style={{ fontSize: '13px', color: getStateInfo(selectedCard).color, fontFamily: font.mono, fontWeight: 800 }}>{getStateInfo(selectedCard).label}</span>
            </div>
            {selectedCard.labels?.length > 0 && (
              <div>
                <p style={{ margin: '0 0 6px', fontSize: '10px', color: '#fff', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Labels</p>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                  {selectedCard.labels.map(l => <span key={l} style={{ fontSize: '11px', color: '#fff', background: color.s3, border: `1px solid ${color.border2}`, borderRadius: '4px', padding: '3px 8px', fontFamily: font.mono, fontWeight: 700 }}>#{l}</span>)}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modales */}
      {stageCard && <StageQuickModal card={stageCard} allStates={allStates} onMove={handleStageMove} onClose={() => setStageCard(null)} />}
      {editCard  && <EditCardModal   card={editCard}  onClose={() => setEditCard(null)} />}
      {editEpic  && epic && <EditEpicModal epic={epic} areaId={areaId} onClose={() => setEditEpic(false)} />}
    </div>
  );
}
