import { useState, useEffect, useRef, useMemo } from 'react';
import { useQueries } from '@tanstack/react-query';
import {
  DndContext, DragOverlay, closestCenter,
  PointerSensor, useSensor, useSensors, useDroppable,
} from '@dnd-kit/core';
import {
  SortableContext, useSortable,
  verticalListSortingStrategy, arrayMove,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { color, font, radius, getAreaHex } from '../../shared/tokens';
import { useUIStore } from '../../shared/store/useUIStore';
import { useCards, usePromoteCard, useMoveTriageStage } from '../../entities/card/hooks/useCards';
import { useAreas } from '../../entities/area/hooks/useAreas';
import { useSpaces } from '../../entities/space/hooks/useSpaces';
import { useEpicsBySpace } from '../../entities/epic/hooks/useEpics';
import { projectsApi } from '../../api/projects';
import PriorityBadge from '../../shared/components/PriorityBadge';
import EditCardModal from '../../shared/components/modals/EditCardModal';

const STAGES = [
  { id: 'inbox',      label: 'INBOX',      accent: '#888888', desc: 'Captura sin clasificar'   },
  { id: 'refinement', label: 'REFINEMENT', accent: '#F5C518', desc: 'En análisis'               },
  { id: 'backlog',    label: 'BACKLOG',    accent: '#8B5CF6', desc: 'Listo para planificar'     },
];

// ─── TriageCard ───────────────────────────────────────────────────────────────

function TriageCard({ card, areas, epic, project, onClick, onPromote, isDragOverlay = false }) {
  const [hov, setHov] = useState(false);
  const area = areas.find(a => a.id === card.area_id);
  const hex  = getAreaHex(area?.color_id);

  return (
    <div
      onClick={!isDragOverlay && onClick ? () => onClick(card) : undefined}
      onMouseEnter={() => !isDragOverlay && setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        borderRadius:  radius.md,
        background:    hov ? color.s3 : color.s2,
        border:        `1px solid ${hov ? 'rgba(255,255,255,0.12)' : color.border}`,
        cursor:        isDragOverlay ? 'grabbing' : 'grab',
        transition:    `background 0.12s, border-color 0.12s, box-shadow 0.12s`,
        opacity:       isDragOverlay ? 1 : 0,
        animation:     isDragOverlay ? 'none' : `slideInUp 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards`,
        userSelect:    'none',
        overflow:      'hidden',
      }}
    >
      {/* Area strip */}
      {area && (
        <div style={{
          background:     `${hex}12`,
          borderBottom:   `1px solid ${hex}24`,
          padding:        '5px 14px',
          display:        'flex',
          justifyContent: 'space-between',
          alignItems:     'center',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <div aria-hidden="true" style={{ width: '5px', height: '5px', borderRadius: '50%', background: hex, flexShrink: 0, boxShadow: `0 0 4px ${hex}50` }} />
            <span style={{ fontSize: '9px', color: hex, fontWeight: 700, letterSpacing: '0.06em', textTransform: 'uppercase', fontFamily: font.sans }}>
              {area.name}
            </span>
          </div>
          <PriorityBadge value={card.priority} />
        </div>
      )}

      {/* Body */}
      <div style={{ padding: area ? '10px 14px 10px' : '12px 14px 10px' }}>
        {area ? (
          <p style={{ margin: '0 0 6px', fontSize: '13px', color: color.text, fontWeight: 700, fontFamily: font.sans, lineHeight: '1.35' }}>
            {card.title}
          </p>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <p style={{ margin: 0, fontSize: '13px', color: color.text, fontWeight: 700, fontFamily: font.sans, flex: 1, lineHeight: '1.35' }}>
              {card.title}
            </p>
            <PriorityBadge value={card.priority} size="xs" />
          </div>
        )}

        {card.description && (
          <p style={{
            margin: '0 0 8px', fontSize: '11px', color: color.muted, fontFamily: font.sans, lineHeight: '1.55',
            display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden',
          }}>
            {card.description}
          </p>
        )}

        {(project || epic) && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '8px', overflow: 'hidden', minWidth: 0 }}>
            {project && (
              <span style={{ fontSize: '10px', color: color.muted, fontFamily: font.mono, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', flex: '1 1 0', minWidth: 0 }}>
                {project.name}
              </span>
            )}
            {project && epic && (
              <span aria-hidden="true" style={{ color: color.muted2, fontSize: '10px', flexShrink: 0 }}>›</span>
            )}
            {epic && (
              <span style={{ fontSize: '10px', color: color.muted2, fontFamily: font.mono, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', flex: '1 1 0', minWidth: 0 }}>
                {epic.name}
              </span>
            )}
          </div>
        )}

        {card.labels?.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {card.labels.map(l => (
              <span key={l} style={{ fontSize: '9px', color: color.muted, background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: radius.xs, padding: '2px 6px', fontFamily: font.mono }}>
                #{l}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Footer: promote button only for backlog */}
      {!isDragOverlay && card.pre_workflow_stage === 'backlog' && (
        <div
          onPointerDown={e => e.stopPropagation()}
          onClick={e => e.stopPropagation()}
          style={{ borderTop: `1px solid ${color.border}`, padding: '0 14px', display: 'flex', justifyContent: 'flex-end', alignItems: 'center', minHeight: '44px' }}
        >
          <button
            onClick={onPromote}
            style={{
              background:   `${color.yellow}18`,
              border:       `1px solid ${color.yellow}40`,
              color:        color.yellow,
              borderRadius: '5px',
              padding:      '6px 12px',
              cursor:       'pointer',
              fontSize:     '10px',
              fontFamily:   font.mono,
              fontWeight:   700,
              minHeight:    '44px',
              display:      'flex',
              alignItems:   'center',
            }}
          >
            → Workflow
          </button>
        </div>
      )}
    </div>
  );
}

// ─── SortableTriageCard ───────────────────────────────────────────────────────

function SortableTriageCard({ card, areas, epic, project, onClick, onPromote }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: card.id });
  const [focused, setFocused] = useState(false);

  return (
    <div
      ref={setNodeRef}
      {...attributes}
      {...listeners}
      role="article"
      aria-label={card.title}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={{
        transform:     CSS.Transform.toString(transform),
        transition,
        opacity:       isDragging ? 0 : 1,
        touchAction:   'none',
        outline:       focused ? `2px solid ${color.yellow}` : 'none',
        outlineOffset: focused ? '2px' : '0',
        borderRadius:  radius.md,
      }}
    >
      <TriageCard
        card={card}
        areas={areas}
        epic={epic}
        project={project}
        onClick={onClick}
        onPromote={onPromote}
      />
    </div>
  );
}

// ─── TriageColumn ─────────────────────────────────────────────────────────────

function TriageColumn({ id, label, accent, desc, cards, areas, epicById, projectById, onCardClick, onPromote }) {
  const { setNodeRef, isOver } = useDroppable({ id });

  return (
    <div style={{
      flex:          1,
      minWidth:      '240px',
      background:    color.s1,
      borderTop:     `4px solid ${accent}`,
      borderRight:   `1px solid ${isOver ? `${accent}80` : color.border}`,
      borderBottom:  `1px solid ${isOver ? `${accent}80` : color.border}`,
      borderLeft:    `1px solid ${isOver ? `${accent}80` : color.border}`,
      borderRadius:  '12px',
      display:       'flex',
      flexDirection: 'column',
      overflow:      'hidden',
      transition:    'border-right-color 150ms, border-bottom-color 150ms, border-left-color 150ms, box-shadow 150ms',
      boxShadow:     isOver ? `0 0 0 2px ${accent}30` : 'none',
    }}>
      {/* Header */}
      <div style={{ padding: '12px 14px', borderBottom: `1px solid ${color.border}`, background: '#0d0d0d', flexShrink: 0 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
          <span style={{ fontSize: '12px', fontWeight: 800, color: accent, fontFamily: font.mono, letterSpacing: '0.1em' }}>{label}</span>
          <span style={{ background: accent, color: accent === '#888888' ? '#fff' : '#000', fontSize: '12px', fontWeight: 800, padding: '2px 10px', borderRadius: '8px', fontFamily: font.mono }}>{cards.length}</span>
        </div>
        <p style={{ margin: 0, fontSize: '11px', color: '#aaa', fontFamily: font.sans, fontWeight: 600 }}>{desc}</p>
      </div>

      {/* Cards */}
      <SortableContext items={cards.map(c => c.id)} strategy={verticalListSortingStrategy}>
        <div ref={setNodeRef} style={{ padding: '8px', display: 'flex', flexDirection: 'column', gap: '6px', overflowY: 'auto', flex: 1 }}>
          {cards.length === 0 ? (
            <div style={{ border: `1px dashed ${isOver ? `${accent}60` : color.border2}`, borderRadius: '8px', padding: '24px 8px', textAlign: 'center', color: isOver ? accent : '#888', fontSize: '12px', fontFamily: font.sans, fontWeight: 700, transition: 'all 150ms' }}>
              {isOver ? 'Soltar aquí' : 'vacío'}
            </div>
          ) : (
            cards.map(c => {
              const epic    = c.epic_id ? epicById[c.epic_id] ?? null : null;
              const project = c.project_id
                ? projectById[c.project_id] ?? null
                : (epic?.project_id ? projectById[epic.project_id] ?? null : null);
              return (
                <SortableTriageCard
                  key={c.id}
                  card={c}
                  areas={areas}
                  epic={epic}
                  project={project}
                  onClick={onCardClick}
                  onPromote={() => onPromote(c)}
                />
              );
            })
          )}
        </div>
      </SortableContext>
    </div>
  );
}

// ─── TriageView ───────────────────────────────────────────────────────────────

export default function TriageView() {
  const activeSpaceId = useUIStore(s => s.activeSpaceId);
  const { data: spaces = [] } = useSpaces();
  const { data: cards  = [] } = useCards(activeSpaceId);
  const { data: areas  = [] } = useAreas();
  const { mutate: promoteCard     } = usePromoteCard(activeSpaceId);
  const { mutate: moveTriageStage } = useMoveTriageStage(activeSpaceId);

  const [editCard,      setEditCard]      = useState(null);
  const [promoteTarget, setPromoteTarget] = useState(null);
  const [activeDragId,  setActiveDragId]  = useState(null);
  const [dragError,     setDragError]     = useState(null);

  const space     = spaces.find(s => s.id === activeSpaceId);
  const allStates = space?.workflow_states ?? [];

  // ── Epic / project data (same pattern as WorkspaceLayout) ─────────────────
  const { data: epics = [] } = useEpicsBySpace(activeSpaceId);
  const epicById = useMemo(
    () => Object.fromEntries(epics.map(e => [e.id, e])),
    [epics],
  );
  const projectIds = useMemo(
    () => [...new Set(epics.map(e => e.project_id).filter(Boolean))],
    [epics],
  );
  const projectResults = useQueries({
    queries: projectIds.map(id => ({
      queryKey: ['project', id],
      queryFn:  () => projectsApi.getById(id),
    })),
  });
  const projectResultsKey = projectResults.map(r => r.data?.id ?? '').join(',');
  const projectById = useMemo(() => {
    const map = {};
    projectResults.forEach(r => { if (r.data?.id) map[r.data.id] = r.data; });
    return map;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectResultsKey]);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
  );

  // Derived: pre-workflow cards
  const preCards = cards.filter(c => c.pre_workflow_stage);

  const [stageOrder, setStageOrder] = useState(() => {
    const init = {};
    STAGES.forEach(s => {
      init[s.id] = preCards.filter(c => c.pre_workflow_stage === s.id).map(c => c.id);
    });
    return init;
  });

  const orderRef          = useRef({});
  const sourceRef         = useRef(null);
  const snapshotRef       = useRef(null);
  const dragErrorTimerRef = useRef(null);

  useEffect(() => () => {
    if (dragErrorTimerRef.current) clearTimeout(dragErrorTimerRef.current);
  }, []);

  useEffect(() => {
    setStageOrder(prev => {
      const next = {};
      STAGES.forEach(s => {
        const existing = prev[s.id] ?? [];
        const ids      = preCards.filter(c => c.pre_workflow_stage === s.id).map(c => c.id);
        next[s.id]     = [
          ...existing.filter(id => ids.includes(id)),
          ...ids.filter(id => !existing.includes(id)),
        ];
      });
      return next;
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cards, activeSpaceId]);

  useEffect(() => { orderRef.current = stageOrder; }, [stageOrder]);

  const getStageCards = (stageId) => {
    const ids = stageOrder[stageId] ?? [];
    return ids.map(id => preCards.find(c => c.id === id)).filter(Boolean);
  };

  const handleDragStart = ({ active }) => {
    setActiveDragId(active.id);
    const order = orderRef.current;
    sourceRef.current   = Object.keys(order).find(id => order[id].includes(active.id)) ?? null;
    snapshotRef.current = Object.fromEntries(Object.entries(order).map(([k, v]) => [k, [...v]]));
  };

  const handleDragOver = ({ active, over }) => {
    if (!over) return;
    const activeId = active.id;
    const overId   = over.id;
    const order    = orderRef.current;

    const srcId  = Object.keys(order).find(id => order[id].includes(activeId));
    const dstId  = STAGES.find(s => s.id === overId)?.id
      ?? Object.keys(order).find(id => order[id].includes(overId));

    if (!srcId || !dstId || srcId === dstId) return;

    setStageOrder(prev => {
      const src = prev[srcId].filter(id => id !== activeId);
      const dst = [...(prev[dstId] ?? [])];
      const idx = dst.indexOf(overId);
      dst.splice(idx === -1 ? dst.length : idx, 0, activeId);
      return { ...prev, [srcId]: src, [dstId]: dst };
    });
  };

  const handleDragEnd = ({ active, over }) => {
    setActiveDragId(null);

    if (!over) {
      if (snapshotRef.current) setStageOrder(snapshotRef.current);
      return;
    }

    const activeId     = active.id;
    const overId       = over.id;
    const originalStage = sourceRef.current;
    const snapshot      = snapshotRef.current;
    const order         = orderRef.current;

    const currentStage = Object.keys(order).find(id => order[id].includes(activeId));
    if (!originalStage || !currentStage) return;

    if (originalStage === currentStage) {
      const isOverCol = STAGES.some(s => s.id === overId);
      if (!isOverCol && activeId !== overId) {
        setStageOrder(prev => {
          const ids  = [...prev[currentStage]];
          const from = ids.indexOf(activeId);
          const to   = ids.indexOf(overId);
          if (from === -1 || to === -1 || from === to) return prev;
          return { ...prev, [currentStage]: arrayMove(ids, from, to) };
        });
      }
    } else {
      moveTriageStage({ cardId: activeId, stage: currentStage }, {
        onError: (err) => {
          setStageOrder(snapshot);
          const msg = err?.response?.data?.detail ?? 'Movimiento no permitido';
          setDragError(msg);
          if (dragErrorTimerRef.current) clearTimeout(dragErrorTimerRef.current);
          dragErrorTimerRef.current = setTimeout(() => setDragError(null), 4000);
        },
      });
    }
  };

  const handlePromote = (stateId) => {
    if (!promoteTarget) return;
    const target = promoteTarget;
    setPromoteTarget(null);
    promoteCard(
      { cardId: target.id, targetStateId: stateId },
      { onError: () => setDragError('No se pudo mover la card al workflow') },
    );
  };

  const activeDragCard = activeDragId ? preCards.find(c => c.id === activeDragId) : null;

  return (
    <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        {/* Columns */}
        <div style={{ flex: 1, display: 'flex', gap: '12px', padding: '16px', overflowX: 'auto', overflowY: 'hidden' }}>
          {STAGES.map(({ id, label, accent, desc }) => (
            <TriageColumn
              key={id}
              id={id}
              label={label}
              accent={accent}
              desc={desc}
              cards={getStageCards(id)}
              areas={areas}
              epicById={epicById}
              projectById={projectById}
              onCardClick={setEditCard}
              onPromote={c => setPromoteTarget(c)}
            />
          ))}
        </div>

        <DragOverlay dropAnimation={{ duration: 180, easing: 'cubic-bezier(0.18, 0.67, 0.6, 1.22)' }}>
          {activeDragCard ? (
            <TriageCard
              card={activeDragCard}
              areas={areas}
              epic={activeDragCard.epic_id ? epicById[activeDragCard.epic_id] ?? null : null}
              project={
                activeDragCard.project_id
                  ? projectById[activeDragCard.project_id] ?? null
                  : (activeDragCard.epic_id && epicById[activeDragCard.epic_id]?.project_id
                      ? projectById[epicById[activeDragCard.epic_id].project_id] ?? null
                      : null)
              }
              isDragOverlay
            />
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Promote modal */}
      {promoteTarget && (
        <>
          <div style={{ position: 'fixed', inset: 0, background: '#00000090', zIndex: 300 }} onClick={() => setPromoteTarget(null)} />
          <div style={{ position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', width: '320px', background: color.s1, border: `1px solid ${color.border}`, borderTop: `3px solid ${color.yellow}`, borderRadius: '12px', padding: '20px', zIndex: 301, boxShadow: '0 30px 80px #000' }}>
            <p style={{ margin: '0 0 4px', fontSize: '11px', color: '#fff', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Mover al Workflow</p>
            <p style={{ margin: '0 0 14px', fontSize: '12px', color: '#ccc', fontFamily: font.sans, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{promoteTarget.title}</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {allStates.map(s => (
                <button key={s.id} onClick={() => handlePromote(s.id)} style={{ background: color.s2, border: `1px solid ${color.border2}`, color: '#fff', borderRadius: '8px', padding: '10px 14px', cursor: 'pointer', fontSize: '13px', fontFamily: font.sans, fontWeight: 700, textAlign: 'left' }}>
                  → {s.name}
                </button>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Error toast */}
      {dragError && (
        <div style={{ position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)', background: '#ef4444', color: '#fff', padding: '10px 20px', borderRadius: '8px', fontSize: '13px', fontFamily: font.mono, fontWeight: 700, zIndex: 999, boxShadow: '0 4px 20px #00000060', whiteSpace: 'nowrap' }}>
          {dragError}
        </div>
      )}

      {editCard && <EditCardModal card={editCard} onClose={() => setEditCard(null)} />}
    </div>
  );
}
