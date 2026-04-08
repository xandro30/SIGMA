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
import { color, font, layout, elevation, motion, radius, getAreaHex, priority as pt } from '../../../shared/tokens';
import PriorityBadge from '../../../shared/components/PriorityBadge';
import EditCardModal from '../../../shared/components/modals/EditCardModal';
import { useUIStore } from '../../../shared/store/useUIStore';
import { useMoveCard } from '../../../entities/card/hooks/useCards';

// ─── Pure display card ────────────────────────────────────────────────────────

function KanbanCard({ card, area, onClick, isDragOverlay = false }) {
  const [hov,     setHov]     = useState(false);
  const [focused, setFocused] = useState(false);
  const hex = getAreaHex(area?.color_id);
  const pr  = pt[card.priority] ?? pt.low;

  return (
    <div
      onClick={onClick ? () => onClick(card) : undefined}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onClick?.(card)}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={{
        padding:       '12px 14px',
        borderRadius:  radius.md,
        background:    hov ? color.s3 : color.s2,
        border:        `1px solid ${hov ? 'rgba(255,255,255,0.12)' : color.border}`,
        borderLeft:    `3px solid ${pr.color}`,
        cursor:        isDragOverlay ? 'grabbing' : 'grab',
        boxShadow:     isDragOverlay ? elevation[3] : hov ? elevation[2] : elevation[1],
        transform:     hov && !isDragOverlay ? 'translateY(-1px)' : 'none',
        transition:    `background ${motion.fast}, border ${motion.fast}, box-shadow ${motion.fast}, transform ${motion.fast}`,
        // Animation only on mount — no animIndex to avoid re-triggering on reorder
        opacity:       isDragOverlay ? 1 : 0,
        animation:     isDragOverlay ? 'none' : `slideInUp 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards`,
        outline:       focused ? `2px solid ${color.yellow}` : 'none',
        outlineOffset: focused ? '2px' : '0',
        userSelect:    'none',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '8px', marginBottom: '6px', alignItems: 'flex-start' }}>
        <p style={{ margin: 0, fontSize: '13px', color: color.text, fontWeight: 700, fontFamily: font.sans, flex: 1, lineHeight: '1.4' }}>
          {card.title}
        </p>
        <PriorityBadge value={card.priority} />
      </div>

      {card.description && (
        <p style={{ margin: '0 0 8px', fontSize: '11px', color: color.muted, fontFamily: font.sans, fontWeight: 400, lineHeight: '1.5',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
          {card.description}
        </p>
      )}

      {card.labels?.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '8px' }}>
          {card.labels.slice(0, 3).map(l => (
            <span key={l} style={{ fontSize: '10px', color: color.muted, background: 'rgba(255,255,255,0.06)', border: `1px solid ${color.border2}`, borderRadius: radius.sm, padding: '2px 7px', fontFamily: font.mono, fontWeight: 500 }}>
              #{l}
            </span>
          ))}
        </div>
      )}

      {area && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <div aria-hidden="true" style={{ width: '6px', height: '6px', borderRadius: '50%', background: hex, flexShrink: 0, boxShadow: `0 0 6px ${hex}80` }} />
          <span style={{ fontSize: '11px', color: color.muted, fontFamily: font.sans, fontWeight: 600 }}>{area.name}</span>
        </div>
      )}
    </div>
  );
}

// ─── Sortable wrapper ─────────────────────────────────────────────────────────

function SortableKanbanCard({ card, area, onClick }) {
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
      <KanbanCard card={card} area={area} onClick={onClick} />
    </div>
  );
}

// ─── Column ───────────────────────────────────────────────────────────────────

function Column({ id, name, cards, areas, onCardClick, animIndex }) {
  const { setNodeRef, isOver } = useDroppable({ id });

  return (
    <div
      ref={setNodeRef}
      style={{
        minWidth:      layout.columnWidth,
        maxWidth:      layout.columnWidth,
        background:    isOver ? `rgba(255,193,7,0.04)` : color.s1,
        border:        `1px solid ${isOver ? `${color.yellow}55` : color.border}`,
        borderTop:     `3px solid ${color.yellow}`,
        borderRadius:  radius.lg,
        display:       'flex',
        flexDirection: 'column',
        flexShrink:    0,
        boxShadow:     isOver ? `0 0 0 2px ${color.yellow}25` : elevation[1],
        opacity:       0,
        animation:     `slideInUp 320ms cubic-bezier(0.16, 1, 0.3, 1) ${animIndex * 50}ms forwards`,
        transition:    `border-color 150ms, background 150ms, box-shadow 150ms`,
      }}
    >
      {/* Header */}
      <div style={{ padding: '10px 14px', borderBottom: `1px solid ${color.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
        <span style={{ fontSize: '11px', fontWeight: 800, letterSpacing: '0.08em', color: isOver ? color.yellow : color.muted, fontFamily: font.mono, textTransform: 'uppercase', transition: `color 150ms` }}>
          {name}
        </span>
        <span style={{ background: color.yellow, color: '#000', fontSize: '11px', fontWeight: 800, padding: '2px 9px', borderRadius: radius.sm, fontFamily: font.mono, minWidth: '26px', textAlign: 'center' }}>
          {cards.length}
        </span>
      </div>

      {/* Cards */}
      <SortableContext items={cards.map(c => c.id)} strategy={verticalListSortingStrategy}>
        <div style={{ padding: '8px', display: 'flex', flexDirection: 'column', gap: '6px', overflowY: 'auto', flex: 1 }}>
          {cards.length === 0 ? (
            <div style={{ border: `1px dashed ${isOver ? `${color.yellow}60` : color.border2}`, borderRadius: radius.md, padding: '24px 8px', textAlign: 'center', color: isOver ? color.yellow : color.muted2, fontSize: '11px', fontFamily: font.sans, fontWeight: 500, transition: 'all 150ms' }}>
              {isOver ? 'Soltar aquí' : 'vacío'}
            </div>
          ) : (
            cards.map(c => (
              <SortableKanbanCard
                key={c.id}
                card={c}
                area={areas?.find(a => a.id === c.area_id)}
                onClick={onCardClick}
              />
            ))
          )}
        </div>
      </SortableContext>
    </div>
  );
}

// ─── Board ────────────────────────────────────────────────────────────────────

export default function KanbanBoard({ space, cards, areas }) {
  const activeSpaceId    = useUIStore(s => s.activeSpaceId);
  const activeAreaFilter = useUIStore(s => s.activeAreaFilter);
  const [editCard,      setEditCard]      = useState(null);
  const [dragError,     setDragError]     = useState(null);
  const [activeDragId,  setActiveDragId]  = useState(null);
  const { mutate: moveCard } = useMoveCard(activeSpaceId);
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } })
  );

  // Derived values — computed before columnOrder useState for lazy init
  const wCards = (activeAreaFilter === 'all' ? cards : cards.filter(c => c.area_id === activeAreaFilter))
    .filter(c => c.workflow_state_id);
  const cols = (space?.workflow_states ?? []).map(s => ({ id: s.id, name: s.name }));

  // In-memory order: { [colId]: [cardId, ...] }
  // Lazy init avoids empty-column flash on first render
  const [columnOrder, setColumnOrder] = useState(() => {
    const init = {};
    cols.forEach(col => {
      init[col.id] = wCards.filter(c => c.workflow_state_id === col.id).map(c => c.id);
    });
    return init;
  });

  const orderRef   = useRef({});
  const sourceRef  = useRef(null);
  const snapshotRef = useRef(null);

  // Sync when cards or space change (new/removed cards, space load)
  useEffect(() => {
    setColumnOrder(prev => {
      const next = {};
      cols.forEach(col => {
        const existing = prev[col.id] ?? [];
        const colIds   = wCards.filter(c => c.workflow_state_id === col.id).map(c => c.id);
        next[col.id]   = [
          ...existing.filter(id => colIds.includes(id)),
          ...colIds.filter(id => !existing.includes(id)),
        ];
      });
      return next;
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cards, space?.id]);

  useEffect(() => { orderRef.current = columnOrder; }, [columnOrder]);

  const getColCards = (colId) => {
    const ids = columnOrder[colId] ?? [];
    return ids.map(id => wCards.find(c => c.id === id)).filter(Boolean);
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

    const srcColId  = Object.keys(order).find(id => order[id].includes(activeId));
    const destColId = cols.find(c => c.id === overId)?.id
      ?? Object.keys(order).find(id => order[id].includes(overId));

    if (!srcColId || !destColId || srcColId === destColId) return;

    setColumnOrder(prev => {
      const src = prev[srcColId].filter(id => id !== activeId);
      const dst = [...(prev[destColId] ?? [])];
      const idx = dst.indexOf(overId);
      dst.splice(idx === -1 ? dst.length : idx, 0, activeId);
      return { ...prev, [srcColId]: src, [destColId]: dst };
    });
  };

  const handleDragEnd = ({ active, over }) => {
    setActiveDragId(null);

    if (!over) {
      if (snapshotRef.current) setColumnOrder(snapshotRef.current);
      return;
    }

    const activeId      = active.id;
    const overId        = over.id;
    const originalColId = sourceRef.current;
    const snapshot      = snapshotRef.current;
    const order         = orderRef.current;

    const currentColId = Object.keys(order).find(id => order[id].includes(activeId));
    if (!originalColId || !currentColId) return;

    if (originalColId === currentColId) {
      const isOverCol = cols.some(c => c.id === overId);
      if (!isOverCol && activeId !== overId) {
        setColumnOrder(prev => {
          const ids  = [...prev[currentColId]];
          const from = ids.indexOf(activeId);
          const to   = ids.indexOf(overId);
          if (from === -1 || to === -1 || from === to) return prev;
          return { ...prev, [currentColId]: arrayMove(ids, from, to) };
        });
      }
    } else {
      moveCard({ cardId: activeId, targetStateId: currentColId }, {
        onError: (err) => {
          setColumnOrder(snapshot);
          const msg = err?.response?.data?.detail ?? 'Movimiento no permitido por el workflow';
          setDragError(msg);
          setTimeout(() => setDragError(null), 4000);
        },
      });
    }
  };

  const activeDragCard = activeDragId ? wCards.find(c => c.id === activeDragId) : null;

  return (
    <>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragOver={handleDragOver}
        onDragEnd={handleDragEnd}
      >
        <div style={{ display: 'flex', gap: '10px', padding: '16px', overflowX: 'auto', overflowY: 'hidden', flex: 1 }}>
          {cols.map((c, i) => (
            <Column
              key={c.id}
              id={c.id}
              name={c.name}
              cards={getColCards(c.id)}
              areas={areas}
              onCardClick={setEditCard}
              animIndex={i}
            />
          ))}
        </div>

        <DragOverlay dropAnimation={{ duration: 180, easing: 'cubic-bezier(0.18, 0.67, 0.6, 1.22)' }}>
          {activeDragCard ? (
            <KanbanCard
              card={activeDragCard}
              area={areas?.find(a => a.id === activeDragCard.area_id)}
              isDragOverlay
            />
          ) : null}
        </DragOverlay>
      </DndContext>

      {dragError && (
        <div style={{ position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)', background: '#ef4444', color: '#fff', padding: '10px 20px', borderRadius: '8px', fontSize: '13px', fontFamily: font.mono, fontWeight: 700, zIndex: 999, boxShadow: '0 4px 20px #00000060', whiteSpace: 'nowrap' }}>
          {dragError}
        </div>
      )}

      {editCard && <EditCardModal card={editCard} onClose={() => setEditCard(null)} />}
    </>
  );
}
