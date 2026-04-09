import { useState, useEffect, useRef } from 'react';
import {
  DndContext, DragOverlay, closestCenter,
  PointerSensor, useSensor, useSensors, useDroppable,
} from '@dnd-kit/core';
import {
  SortableContext, useSortable,
  verticalListSortingStrategy, arrayMove,
} from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { color, font, getAreaHex, priority as pt } from '../../shared/tokens';
import { useUIStore } from '../../shared/store/useUIStore';
import { useCards, usePromoteCard, useMoveTriageStage } from '../../entities/card/hooks/useCards';
import { useAreas } from '../../entities/area/hooks/useAreas';
import { useSpaces } from '../../entities/space/hooks/useSpaces';
import PriorityBadge from '../../shared/components/PriorityBadge';
import EditCardModal from '../../shared/components/modals/EditCardModal';

const STAGES = [
  { id: 'inbox',      label: 'INBOX',      accent: '#888888', desc: 'Captura sin clasificar'   },
  { id: 'refinement', label: 'REFINEMENT', accent: '#F5C518', desc: 'En análisis'               },
  { id: 'backlog',    label: 'BACKLOG',    accent: '#8B5CF6', desc: 'Listo para planificar'     },
];

// ─── Pure display card ────────────────────────────────────────────────────────

function TriageCard({ card, areas, isSelected, onSelect, onEdit, onPromote, isDragOverlay = false }) {
  const area  = areas.find(a => a.id === card.area_id);
  const hex   = getAreaHex(area?.color_id);
  const pr    = pt[card.priority] ?? pt.low;

  return (
    <div
      style={{
        padding:      '12px',
        borderRadius: '9px',
        cursor:       isDragOverlay ? 'grabbing' : 'grab',
        background:   isSelected ? color.s3 : color.s2,
        borderTop:    `1px solid ${isSelected ? color.yellow : color.border}`,
        borderRight:  `1px solid ${isSelected ? color.yellow : color.border}`,
        borderBottom: `1px solid ${isSelected ? color.yellow : color.border}`,
        borderLeft:   `4px solid ${pr.color}`,
        // Entrance animation — constant delay prevents re-trigger on reorder
        opacity:      isDragOverlay ? 1 : 0,
        animation:    isDragOverlay ? 'none' : `slideInUp 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards`,
        transition:   'background 0.12s, border-color 0.12s',
        userSelect:   'none',
        boxShadow:    isDragOverlay ? '0 8px 30px #00000060' : 'none',
      }}
    >
      {/* Card body — click to select */}
      <div onClick={isDragOverlay ? undefined : () => onSelect(card)}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '8px', marginBottom: '8px', alignItems: 'flex-start' }}>
          <p style={{ margin: 0, fontSize: '13px', color: '#fff', fontFamily: font.sans, fontWeight: 700, lineHeight: '1.4', flex: 1 }}>{card.title}</p>
          <PriorityBadge value={card.priority} />
        </div>
        {card.description && (
          <p style={{ margin: '0 0 8px', fontSize: '11px', color: '#ccc', fontFamily: font.sans, fontWeight: 600 }}>
            {card.description.slice(0, 80)}{card.description.length > 80 ? '…' : ''}
          </p>
        )}
        {area && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '8px' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: hex }} />
            <span style={{ fontSize: '11px', color: '#fff', fontFamily: font.mono, fontWeight: 700 }}>{area.name}</span>
          </div>
        )}
      </div>

      {/* Action buttons */}
      {!isDragOverlay && (
        <div style={{ display: 'flex', gap: '5px', borderTop: `1px solid ${color.border}`, paddingTop: '8px', flexWrap: 'wrap' }}>
          <button
            onClick={e => { e.stopPropagation(); onEdit(card); }}
            style={{ background: 'transparent', border: `1px solid ${color.border2}`, color: '#fff', borderRadius: '5px', padding: '3px 8px', cursor: 'pointer', fontSize: '10px', fontFamily: font.mono, fontWeight: 700, marginLeft: 'auto' }}
          >
            ✏
          </button>
          {card.pre_workflow_stage === 'backlog' && (
            <button
              onClick={e => { e.stopPropagation(); onPromote(card); }}
              style={{ background: color.yellow, border: 'none', color: '#000', borderRadius: '5px', padding: '3px 10px', cursor: 'pointer', fontSize: '10px', fontFamily: font.mono, fontWeight: 800 }}
            >
              → Workflow
            </button>
          )}
        </div>
      )}
    </div>
  );
}

// ─── Sortable wrapper ─────────────────────────────────────────────────────────

function SortableTriageCard({ card, areas, isSelected, onSelect, onEdit, onPromote }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: card.id });

  return (
    <div
      ref={setNodeRef}
      {...attributes}
      {...listeners}
      style={{
        transform:   CSS.Transform.toString(transform),
        transition,
        opacity:     isDragging ? 0 : 1,
        touchAction: 'none',
      }}
    >
      <TriageCard
        card={card}
        areas={areas}
        isSelected={isSelected}
        onSelect={onSelect}
        onEdit={onEdit}
        onPromote={onPromote}
      />
    </div>
  );
}

// ─── Column ───────────────────────────────────────────────────────────────────

function TriageColumn({ id, label, accent, desc, cards, areas, selectedId, onSelect, onEdit, onPromote }) {
  const { setNodeRef, isOver } = useDroppable({ id });

  return (
    <div style={{ flex: 1, minWidth: '240px', background: color.s1, border: `1px solid ${isOver ? `${accent}80` : color.border}`, borderTop: `4px solid ${accent}`, borderRadius: '12px', display: 'flex', flexDirection: 'column', overflow: 'hidden', transition: 'border-color 150ms, box-shadow 150ms', boxShadow: isOver ? `0 0 0 2px ${accent}30` : 'none' }}>
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
            cards.map(c => (
              <SortableTriageCard
                key={c.id}
                card={c}
                areas={areas}
                isSelected={selectedId === c.id}
                onSelect={onSelect}
                onEdit={onEdit}
                onPromote={onPromote}
              />
            ))
          )}
        </div>
      </SortableContext>
    </div>
  );
}

// ─── View ─────────────────────────────────────────────────────────────────────

export default function TriageView() {
  const activeSpaceId = useUIStore(s => s.activeSpaceId);
  const { data: spaces = [] } = useSpaces();
  const { data: cards  = [] } = useCards(activeSpaceId);
  const { data: areas  = [] } = useAreas();
  const { mutate: promoteCard     } = usePromoteCard(activeSpaceId);
  const { mutate: moveTriageStage } = useMoveTriageStage(activeSpaceId);

  const [selected,      setSelected]      = useState(null);
  const [editCard,      setEditCard]      = useState(null);
  const [promoteTarget, setPromoteTarget] = useState(null);
  const [activeDragId,  setActiveDragId]  = useState(null);
  const [dragError,     setDragError]     = useState(null);

  const space     = spaces.find(s => s.id === activeSpaceId);
  const allStates = space?.workflow_states ?? [];

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } })
  );

  // Derived: pre-workflow cards (computed before stageOrder useState for lazy init)
  const preCards = cards.filter(c => c.pre_workflow_stage);

  // In-memory order: { [stageId]: [cardId, ...] }
  // Lazy init avoids "vacío" flash on first render
  const [stageOrder, setStageOrder] = useState(() => {
    const init = {};
    STAGES.forEach(s => {
      init[s.id] = preCards.filter(c => c.pre_workflow_stage === s.id).map(c => c.id);
    });
    return init;
  });

  const orderRef    = useRef({});
  const sourceRef   = useRef(null);
  const snapshotRef = useRef(null);

  // Sync when cards or space change
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
    const originalStge = sourceRef.current;
    const snapshot     = snapshotRef.current;
    const order        = orderRef.current;

    const currentStage = Object.keys(order).find(id => order[id].includes(activeId));
    if (!originalStge || !currentStage) return;

    if (originalStge === currentStage) {
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
          setTimeout(() => setDragError(null), 4000);
        },
      });
    }
  };

  const handlePromote = (stateId) => {
    if (!promoteTarget) return;
    promoteCard({ cardId: promoteTarget.id, targetStateId: stateId });
    setPromoteTarget(null);
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
              selectedId={selected?.id}
              onSelect={c => setSelected(prev => prev?.id === c.id ? null : c)}
              onEdit={setEditCard}
              onPromote={c => setPromoteTarget(c)}
            />
          ))}
        </div>

        <DragOverlay dropAnimation={{ duration: 180, easing: 'cubic-bezier(0.18, 0.67, 0.6, 1.22)' }}>
          {activeDragCard ? (
            <TriageCard
              card={activeDragCard}
              areas={areas}
              isSelected={false}
              onSelect={() => {}}
              onEdit={() => {}}
              onPromote={() => {}}
              isDragOverlay
            />
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Detail panel */}
      {selected && !promoteTarget && !editCard && (
        <div style={{ width: '280px', flexShrink: 0, borderLeft: `1px solid ${color.border}`, background: '#0d0d0d', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          <div style={{ padding: '12px 16px', borderBottom: `1px solid ${color.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '11px', color: '#fff', fontFamily: font.mono, fontWeight: 800, letterSpacing: '0.1em' }}>DETALLE</span>
            <div style={{ display: 'flex', gap: '6px' }}>
              <button onClick={() => setEditCard(selected)} style={{ background: 'none', border: `1px solid ${color.border2}`, borderRadius: '5px', color: color.yellow, cursor: 'pointer', padding: '3px 9px', fontSize: '11px', fontFamily: font.mono, fontWeight: 700 }}>✏ Editar</button>
              <button onClick={() => setSelected(null)} style={{ background: 'none', border: 'none', color: '#fff', cursor: 'pointer', fontSize: '18px' }}>✕</button>
            </div>
          </div>
          <div style={{ padding: '16px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <PriorityBadge value={selected.priority} size="md" />
            <h3 style={{ margin: 0, fontSize: '15px', color: '#fff', fontFamily: font.sans, fontWeight: 800, lineHeight: '1.4' }}>{selected.title}</h3>
            {selected.description && <p style={{ margin: 0, fontSize: '12px', color: '#ccc', fontFamily: font.sans, fontWeight: 600, lineHeight: '1.6' }}>{selected.description}</p>}
            <div style={{ padding: '10px', background: color.s2, borderRadius: '8px', border: `1px solid ${color.border}` }}>
              <p style={{ margin: '0 0 3px', fontSize: '10px', color: '#fff', fontFamily: font.mono, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em' }}>Stage</p>
              <span style={{ fontSize: '13px', fontFamily: font.mono, fontWeight: 800, color: STAGES.find(s => s.id === selected.pre_workflow_stage)?.accent ?? '#888' }}>
                {selected.pre_workflow_stage?.toUpperCase()}
              </span>
            </div>
            {selected.labels?.length > 0 && (
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                {selected.labels.map(l => <span key={l} style={{ fontSize: '11px', color: '#fff', background: color.s3, border: `1px solid ${color.border2}`, borderRadius: '4px', padding: '3px 8px', fontFamily: font.mono, fontWeight: 700 }}>#{l}</span>)}
              </div>
            )}
          </div>
        </div>
      )}

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
