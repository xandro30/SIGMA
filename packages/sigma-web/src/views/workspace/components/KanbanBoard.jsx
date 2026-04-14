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
import { tracking as tk } from '../../../entities/tracking/trackingTokens';
import PriorityBadge from '../../../shared/components/PriorityBadge';
import EditCardModal from '../../../shared/components/modals/EditCardModal';
import StartWorkModal from '../../../shared/components/tracking/StartWorkModal';
import StopSessionModal from '../../../shared/components/tracking/StopSessionModal';
import SessionCompletedBanner from '../../../shared/components/tracking/SessionCompletedBanner';
import { useUIStore } from '../../../shared/store/useUIStore';
import { useMoveCard } from '../../../entities/card/hooks/useCards';
import { useActiveSession } from '../../../entities/tracking/hooks/useActiveSession';
import { useTrackingTimer } from '../../../entities/tracking/hooks/useTrackingTimer';
import { useStartSession } from '../../../entities/tracking/hooks/useStartSession';
import { useStopSession } from '../../../entities/tracking/hooks/useStopSession';
import { useCompleteRound } from '../../../entities/tracking/hooks/useCompleteRound';
import { useResumeFromBreak } from '../../../entities/tracking/hooks/useResumeFromBreak';

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatCountdown(secs) {
  const m = String(Math.floor((secs ?? 0) / 60)).padStart(2, '0');
  const s = String((secs ?? 0) % 60).padStart(2, '0');
  return `${m}:${s}`;
}

// ─── StopButton ───────────────────────────────────────────────────────────────

function StopButton({ onClick }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      aria-label="Detener sesión"
      style={{
        background:   hov ? color.s4 : color.s3,
        border:       `1px solid ${hov ? color.border2 : color.border}`,
        color:        hov ? '#999' : '#666',
        width:        '24px',
        height:       '24px',
        borderRadius: '4px',
        cursor:       'pointer',
        display:      'flex',
        alignItems:   'center',
        justifyContent: 'center',
        padding:      0,
        flexShrink:   0,
        transition:   `all ${motion.fast}`,
      }}
    >
      <span style={{ display: 'block', width: '8px', height: '8px', background: hov ? '#999' : '#666', borderRadius: '1px' }} />
    </button>
  );
}

// ─── KanbanCard ───────────────────────────────────────────────────────────────

function KanbanCard({
  card, area, onClick, isDragOverlay = false,
  session, secondsLeft, completedBanner,
  onStartWork, onStop, onResume, onDismissBanner,
}) {
  const [hov,     setHov]     = useState(false);
  const [focused, setFocused] = useState(false);
  const hex = getAreaHex(area?.color_id);
  const pr  = pt[card.priority] ?? pt.low;

  const isWorking = session?.state === 'working';
  const isBreak   = session?.state === 'break';
  const hasSession = isWorking || isBreak;

  // Border left: session state overrides priority color
  const borderLeft = isWorking ? `3px solid ${color.yellow}`
                   : isBreak   ? `3px solid ${color.blue}`
                   :             `3px solid ${pr.color}`;

  return (
    <div
      onClick={onClick ? () => onClick(card) : undefined}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onClick?.(card)}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={{
        borderRadius:  radius.md,
        background:    hov ? color.s3 : color.s2,
        border:        `1px solid ${hov ? 'rgba(255,255,255,0.12)' : color.border}`,
        borderLeft,
        cursor:        isDragOverlay ? 'grabbing' : 'grab',
        boxShadow:     isDragOverlay ? elevation[3] : hov ? elevation[2] : elevation[1],
        transform:     hov && !isDragOverlay ? 'translateY(-1px)' : 'none',
        transition:    `background ${motion.fast}, border ${motion.fast}, box-shadow ${motion.fast}, transform ${motion.fast}`,
        opacity:       isDragOverlay ? 1 : 0,
        animation:     isDragOverlay ? 'none' : `slideInUp 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards`,
        outline:       focused ? `2px solid ${color.yellow}` : 'none',
        outlineOffset: focused ? '2px' : '0',
        userSelect:    'none',
        overflow:      'hidden',
      }}
    >
      {/* Card body — drag zone */}
      <div style={{ padding: '12px 14px 10px' }}>
        {/* Completed banner */}
        {completedBanner && (
          <SessionCompletedBanner
            minutesLogged={completedBanner.minutes}
            onDismiss={onDismissBanner}
          />
        )}

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

      {/* Tracking footer — NOT a drag zone */}
      <div onPointerDown={e => e.stopPropagation()}>
        {!hasSession && (
          <div
            onClick={onStartWork}
            style={{
              borderTop: `1px solid ${color.border}`,
              padding:   '7px 12px',
              textAlign: 'center',
              cursor:    'pointer',
            }}
          >
            <span style={{ color: color.muted, fontSize: '11px', fontWeight: 600, fontFamily: font.sans }}>
              ▶ Start Work
            </span>
          </div>
        )}

        {isWorking && (
          <div style={{
            background:  tk.working.bg,
            borderTop:   `1px solid ${tk.working.borderTop}`,
            padding:     '7px 12px',
            display:     'flex',
            alignItems:  'center',
            justifyContent: 'space-between',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '5px', height: '5px', borderRadius: '50%',
                background: color.yellow,
                boxShadow: `0 0 5px rgba(245,197,24,0.5)`,
                animation: 'pulse 1.5s ease-in-out infinite',
              }} />
              <span style={{ color: color.yellow, fontSize: '13px', fontFamily: font.mono, fontWeight: 700 }}>
                {formatCountdown(secondsLeft)}
              </span>
              <span style={{ color: color.muted2, fontSize: '10px' }}>
                {session.current_round}/{session.num_rounds}
              </span>
            </div>
            <StopButton onClick={onStop} />
          </div>
        )}

        {isBreak && (
          <div style={{
            background:  tk.break.bg,
            borderTop:   `1px solid ${tk.break.borderTop}`,
            padding:     '7px 12px',
            display:     'flex',
            alignItems:  'center',
            justifyContent: 'space-between',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{ width: '5px', height: '5px', borderRadius: '50%', background: color.blue }} />
              <span style={{ color: color.blue, fontSize: '13px', fontFamily: font.mono, fontWeight: 700 }}>
                {formatCountdown(secondsLeft)}
              </span>
              <span style={{ color: color.muted2, fontSize: '10px' }}>descanso</span>
            </div>
            <button
              onClick={onResume}
              style={{
                background:   'rgba(58,123,213,0.12)',
                border:       `1px solid ${color.blueBorder}`,
                color:        color.blue,
                fontSize:     '10px',
                padding:      '3px 10px',
                borderRadius: '4px',
                cursor:       'pointer',
                fontFamily:   font.sans,
                transition:   `all ${motion.fast}`,
              }}
            >
              ▶ Reanudar
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── SortableKanbanCard ───────────────────────────────────────────────────────

function SortableKanbanCard({ card, area, onClick, session, secondsLeft, completedBanner, onStartWork, onStop, onResume, onDismissBanner }) {
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
      <KanbanCard
        card={card}
        area={area}
        onClick={onClick}
        session={session}
        secondsLeft={secondsLeft}
        completedBanner={completedBanner}
        onStartWork={onStartWork}
        onStop={onStop}
        onResume={onResume}
        onDismissBanner={onDismissBanner}
      />
    </div>
  );
}

// ─── Column ───────────────────────────────────────────────────────────────────

function Column({ id, name, cards, areas, onCardClick, animIndex, activeSession, secondsLeft, completedBanner, onStartWork, onStop, onResume, onDismissBanner }) {
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
            cards.map(c => {
              const cardSession = activeSession?.card_id === c.id ? activeSession : null;
              const cardBanner  = completedBanner?.cardId === c.id ? completedBanner : null;
              return (
                <SortableKanbanCard
                  key={c.id}
                  card={c}
                  area={areas?.find(a => a.id === c.area_id)}
                  onClick={onCardClick}
                  session={cardSession}
                  secondsLeft={cardSession ? secondsLeft : null}
                  completedBanner={cardBanner}
                  onStartWork={() => onStartWork(c)}
                  onStop={onStop}
                  onResume={onResume}
                  onDismissBanner={onDismissBanner}
                />
              );
            })
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
  const [startModalCard, setStartModalCard] = useState(null);
  const [stopModalOpen,  setStopModalOpen]  = useState(false);
  const [completedBanner, setCompletedBanner] = useState(null); // { cardId, minutes }

  const { mutate: moveCard }       = useMoveCard(activeSpaceId);
  const { data: activeSession }    = useActiveSession(space?.id);
  const { mutate: startSession }   = useStartSession(space?.id);
  const { mutate: stopSession }    = useStopSession(space?.id);
  const { mutate: completeRound }  = useCompleteRound(space?.id);
  const { mutate: resumeFromBreak } = useResumeFromBreak(space?.id);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } })
  );

  // ── Timer ──────────────────────────────────────────────────────────────────
  const timerInitialSeconds = activeSession
    ? (activeSession.state === 'working'
        ? activeSession.work_minutes * 60
        : activeSession.break_minutes * 60)
    : null;

  // Recovery from page reload: recalculate elapsed time
  const recoveryDoneRef = useRef(false);
  useEffect(() => {
    if (!activeSession || recoveryDoneRef.current) return;
    recoveryDoneRef.current = true;
    if (!activeSession.current_started_at) return;

    const elapsed = Math.floor((Date.now() - new Date(activeSession.current_started_at).getTime()) / 1000);
    const total   = activeSession.state === 'working'
      ? activeSession.work_minutes * 60
      : activeSession.break_minutes * 60;

    if (elapsed >= total) {
      if (activeSession.state === 'working') completeRound();
      else resumeFromBreak();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeSession?.id]);

  const { secondsLeft } = useTrackingTimer(
    timerInitialSeconds,
    () => {
      if (activeSession?.state === 'working') {
        completeRound(undefined, {
          onSuccess: (updated) => {
            // null / completed state → session ended, show banner
            if (!updated || updated.state === 'completed') {
              const totalMinutes = (activeSession.work_minutes ?? 25) * (activeSession.num_rounds ?? 4);
              setCompletedBanner({ cardId: activeSession.card_id, minutes: totalMinutes });
            }
          },
        });
      } else {
        resumeFromBreak();
      }
    }
  );

  // ── Column order ───────────────────────────────────────────────────────────
  const wCards = (activeAreaFilter === 'all' ? cards : cards.filter(c => c.area_id === activeAreaFilter))
    .filter(c => c.workflow_state_id);
  const cols = (space?.workflow_states ?? []).map(s => ({ id: s.id, name: s.name }));

  const [columnOrder, setColumnOrder] = useState(() => {
    const init = {};
    cols.forEach(col => {
      init[col.id] = wCards.filter(c => c.workflow_state_id === col.id).map(c => c.id);
    });
    return init;
  });

  const orderRef    = useRef({});
  const sourceRef   = useRef(null);
  const snapshotRef = useRef(null);

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

  // ── Drag handlers ──────────────────────────────────────────────────────────
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

  // ── Elapsed minutes (for stop modal) ──────────────────────────────────────
  const elapsedMinutes = timerInitialSeconds != null
    ? Math.max(0, Math.floor((timerInitialSeconds - secondsLeft) / 60))
    : 0;

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
              activeSession={activeSession}
              secondsLeft={secondsLeft}
              completedBanner={completedBanner}
              onStartWork={(card) => setStartModalCard(card)}
              onStop={() => setStopModalOpen(true)}
              onResume={() => resumeFromBreak()}
              onDismissBanner={() => setCompletedBanner(null)}
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

      {/* Error toast */}
      {dragError && (
        <div style={{ position: 'fixed', bottom: '24px', left: '50%', transform: 'translateX(-50%)', background: '#ef4444', color: '#fff', padding: '10px 20px', borderRadius: '8px', fontSize: '13px', fontFamily: font.mono, fontWeight: 700, zIndex: 999, boxShadow: '0 4px 20px #00000060', whiteSpace: 'nowrap' }}>
          {dragError}
        </div>
      )}

      {/* Modals */}
      {editCard && <EditCardModal card={editCard} onClose={() => setEditCard(null)} />}

      {startModalCard && (
        <StartWorkModal
          card={startModalCard}
          onConfirm={(data) => {
            startSession({ ...data, card_id: startModalCard.id });
            setStartModalCard(null);
          }}
          onClose={() => setStartModalCard(null)}
        />
      )}

      {stopModalOpen && activeSession && (
        <StopSessionModal
          card={wCards.find(c => c.id === activeSession.card_id)}
          minutesWorked={elapsedMinutes}
          onSave={() => { stopSession(true); setStopModalOpen(false); }}
          onDiscard={() => { stopSession(false); setStopModalOpen(false); }}
          onClose={() => setStopModalOpen(false)}
        />
      )}
    </>
  );
}
