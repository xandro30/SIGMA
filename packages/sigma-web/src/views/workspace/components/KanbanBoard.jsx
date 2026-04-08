import { useState, useMemo } from 'react';
import { color, font, layout, elevation, motion, radius, getAreaHex, priority as pt, PRIORITY_ORDER } from '../../../shared/tokens';
import PriorityBadge from '../../../shared/components/PriorityBadge';
import EditCardModal from '../../../shared/components/modals/EditCardModal';
import { useUIStore } from '../../../shared/store/useUIStore';

function KanbanCard({ card, area, onClick, animIndex }) {
  const [hov,     setHov]     = useState(false);
  const [pressed, setPressed] = useState(false);
  const [focused, setFocused] = useState(false);
  const hex = getAreaHex(area?.color_id);
  const pr  = pt[card.priority] ?? pt.low;

  const cardStyle = {
    padding:       '12px 14px',
    borderRadius:  radius.md,
    background:    hov ? color.s3 : color.s2,
    border:        `1px solid ${hov ? 'rgba(255,255,255,0.12)' : color.border}`,
    borderLeft:    `3px solid ${pr.color}`,
    cursor:        'pointer',
    boxShadow:     hov ? elevation[2] : elevation[1],
    transform:     pressed ? 'translateY(0) scale(0.99)' : hov ? 'translateY(-2px) scale(1.005)' : 'translateY(0) scale(1)',
    transition:    `all ${motion.fast}`,
    opacity:       0,
    animation:     `slideInUp 260ms cubic-bezier(0.16, 1, 0.3, 1) ${animIndex * 35}ms forwards`,
    outline:       focused ? `2px solid ${color.yellow}` : 'none',
    outlineOffset: focused ? '2px' : '0',
  };

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label={`Card: ${card.title}`}
      onClick={() => onClick(card)}
      onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && onClick(card)}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => { setHov(false); setPressed(false); }}
      onMouseDown={() => setPressed(true)}
      onMouseUp={() => setPressed(false)}
      onFocus={() => setFocused(true)}
      onBlur={() => setFocused(false)}
      style={cardStyle}
    >
      {/* Title row */}
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '8px', marginBottom: '6px', alignItems: 'flex-start' }}>
        <p style={{ margin: 0, fontSize: '13px', color: color.text, fontWeight: 700, fontFamily: font.sans, flex: 1, lineHeight: '1.4' }}>
          {card.title}
        </p>
        <PriorityBadge value={card.priority} />
      </div>

      {/* Description */}
      {card.description && (
        <p style={{ margin: '0 0 8px', fontSize: '11px', color: color.muted, fontFamily: font.sans, fontWeight: 400, lineHeight: '1.5',
          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
          {card.description}
        </p>
      )}

      {/* Labels */}
      {card.labels?.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '8px' }}>
          {card.labels.slice(0, 3).map(l => (
            <span key={l} style={{ fontSize: '10px', color: color.muted, background: 'rgba(255,255,255,0.06)', border: `1px solid ${color.border2}`, borderRadius: radius.sm, padding: '2px 7px', fontFamily: font.mono, fontWeight: 500 }}>
              #{l}
            </span>
          ))}
        </div>
      )}

      {/* Area indicator */}
      {area && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <div aria-hidden="true" style={{ width: '6px', height: '6px', borderRadius: '50%', background: hex, flexShrink: 0, boxShadow: `0 0 6px ${hex}80` }} />
          <span style={{ fontSize: '11px', color: color.muted, fontFamily: font.sans, fontWeight: 600 }}>{area.name}</span>
        </div>
      )}
    </div>
  );
}

function Column({ name, isFinish, cards, areas, onCardClick, animIndex }) {
  const accentColor = isFinish ? '#10B981' : color.yellow;
  const total       = cards.length;

  return (
    <div style={{
      minWidth:        layout.columnWidth,
      maxWidth:        layout.columnWidth,
      background:      color.s1,
      border:          `1px solid ${color.border}`,
      borderTop:       `3px solid ${accentColor}`,
      borderRadius:    radius.lg,
      display:         'flex',
      flexDirection:   'column',
      flexShrink:      0,
      boxShadow:       elevation[1],
      opacity:         0,
      animation:       `slideInUp 320ms cubic-bezier(0.16, 1, 0.3, 1) ${animIndex * 50}ms forwards`,
    }}>
      {/* Column header */}
      <div style={{ padding: '10px 14px', borderBottom: `1px solid ${color.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
        <span style={{ fontSize: '11px', fontWeight: 800, letterSpacing: '0.08em', color: color.muted, fontFamily: font.mono, textTransform: 'uppercase' }}>
          {name}
        </span>
        <span style={{ background: accentColor, color: '#000', fontSize: '11px', fontWeight: 800, padding: '2px 9px', borderRadius: radius.sm, fontFamily: font.mono, minWidth: '26px', textAlign: 'center' }}>
          {total}
        </span>
      </div>

      {/* Cards */}
      <div style={{ padding: '8px', display: 'flex', flexDirection: 'column', gap: '6px', overflowY: 'auto', flex: 1 }}>
        {cards.length === 0 ? (
          <div style={{ border: `1px dashed ${color.border2}`, borderRadius: radius.md, padding: '24px 8px', textAlign: 'center', color: color.muted2, fontSize: '11px', fontFamily: font.sans, fontWeight: 500 }}>
            vacío
          </div>
        ) : (
          [...cards]
            .sort((a, b) => (PRIORITY_ORDER[a.priority] ?? 4) - (PRIORITY_ORDER[b.priority] ?? 4))
            .map((c, i) => (
              <KanbanCard
                key={c.id}
                card={c}
                area={areas?.find(a => a.id === c.area_id)}
                onClick={onCardClick}
                animIndex={i}
              />
            ))
        )}
      </div>
    </div>
  );
}

export default function KanbanBoard({ space, cards, areas }) {
  const activeSpaceId    = useUIStore(s => s.activeSpaceId);
  const activeAreaFilter = useUIStore(s => s.activeAreaFilter);
  const [editCard, setEditCard] = useState(null);

  const wCards = (activeAreaFilter === 'all' ? cards : cards.filter(c => c.area_id === activeAreaFilter))
    .filter(c => c.workflow_state_id);

  const cols = (space?.workflow_states ?? []).map(s => ({ id: s.id, name: s.name, isFinish: false }));

  return (
    <>
      <div style={{ display: 'flex', gap: '10px', padding: '16px', overflowX: 'auto', overflowY: 'hidden', flex: 1 }}>
        {cols.map((c, i) => (
          <Column
            key={c.id}
            name={c.name}
            isFinish={c.isFinish}
            cards={wCards.filter(x => x.workflow_state_id === c.id)}
            areas={areas}
            onCardClick={setEditCard}
            animIndex={i}
          />
        ))}
      </div>
      {editCard && <EditCardModal card={editCard} onClose={() => setEditCard(null)} />}
    </>
  );
}
