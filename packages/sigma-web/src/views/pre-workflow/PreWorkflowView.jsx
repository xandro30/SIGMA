import { useState } from 'react';
import { color, font } from '../../shared/tokens';
import { useUIStore } from '../../shared/store/useUIStore';
import { useCards, usePromoteCard } from '../../entities/card/hooks/useCards';
import { useAreas } from '../../entities/area/hooks/useAreas';
import { useSpaces } from '../../entities/space/hooks/useSpaces';
import PriorityBadge from '../../shared/components/PriorityBadge';
import { getAreaHex } from '../../shared/tokens';

const STAGES = [
  { id: 'inbox',      label: 'INBOX',       stageColor: '#666666', desc: 'Captura rápida sin clasificar' },
  { id: 'refinement', label: 'REFINEMENT',  stageColor: '#F5C518', desc: 'En proceso de análisis' },
  { id: 'backlog',    label: 'BACKLOG',      stageColor: '#8B5CF6', desc: 'Listo para planificar' },
];

function PreCard({ card, areas, onPromote, onSelect, isSelected }) {
  const area = areas?.find(a => a.id === card.area_id);
  const hex  = getAreaHex(area?.color_id);
  return (
    <div onClick={() => onSelect(card)} style={{ padding: '10px 12px', borderRadius: '9px', background: isSelected ? color.s3 : color.s2, border: `1px solid ${isSelected ? color.yellow + '60' : color.border}`, cursor: 'pointer', transition: 'all 0.12s' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '8px', marginBottom: '7px' }}>
        <p style={{ margin: 0, fontSize: '12px', color: color.text, fontFamily: font.sans, fontWeight: 500, lineHeight: '1.4', flex: 1 }}>{card.title}</p>
        <PriorityBadge value={card.priority} />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        {area
          ? <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}><div style={{ width: '5px', height: '5px', borderRadius: '50%', background: hex }} /><span style={{ fontSize: '9px', color: color.muted, fontFamily: font.mono }}>{area.name}</span></div>
          : <span style={{ fontSize: '9px', color: color.muted2, fontFamily: font.mono }}>Sin área</span>
        }
        {card.pre_workflow_stage === 'backlog' && (
          <button onClick={e => { e.stopPropagation(); onPromote(card); }} style={{ background: `${color.yellow}18`, border: `1px solid ${color.yellow}40`, color: color.yellow, borderRadius: '5px', padding: '3px 8px', cursor: 'pointer', fontSize: '9px', fontFamily: font.mono, fontWeight: 700 }}>→ Workflow</button>
        )}
      </div>
    </div>
  );
}

export default function PreWorkflowView() {
  const activeSpaceId = useUIStore(s => s.activeSpaceId);
  const { data: spaces  = [] } = useSpaces();
  const { data: cards   = [] } = useCards(activeSpaceId);
  const { data: areas   = [] } = useAreas();
  const { mutate: promoteCard } = usePromoteCard(activeSpaceId);

  const [selectedCard,  setSelectedCard]  = useState(null);
  const [showMoveModal, setShowMoveModal] = useState(false);

  const space = spaces.find(s => s.id === activeSpaceId);
  const allStates = space?.workflow_states ?? [];

  const preCards = cards.filter(c => c.pre_workflow_stage);

  const doPromote = stateId => {
    promoteCard({ cardId: selectedCard.id, targetStateId: stateId });
    setShowMoveModal(false); setSelectedCard(null);
  };

  return (
    <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
      {/* 3 columnas */}
      <div style={{ flex: 1, display: 'flex', gap: '12px', padding: '16px', overflowX: 'auto', overflowY: 'hidden' }}>
        {STAGES.map(({ id, label, stageColor, desc }) => {
          const stageCards = preCards.filter(c => c.pre_workflow_stage === id);
          return (
            <div key={id} style={{ flex: 1, background: color.s1, border: `1px solid ${color.border}`, borderTop: `3px solid ${stageColor}`, borderRadius: '10px', display: 'flex', flexDirection: 'column', minWidth: 0, overflow: 'hidden' }}>
              <div style={{ padding: '10px 14px', borderBottom: `1px solid ${color.border}`, background: `rgba(255,255,255,0.02)` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
                  <span style={{ fontSize: '9px', fontWeight: 800, color: stageColor, fontFamily: font.mono, letterSpacing: '0.1em' }}>{label}</span>
                  <span style={{ background: `${stageColor}20`, color: stageColor, fontSize: '9px', fontWeight: 700, padding: '1px 7px', borderRadius: '8px', fontFamily: font.mono }}>{stageCards.length}</span>
                </div>
                <p style={{ margin: 0, fontSize: '9px', color: color.muted2, fontFamily: font.sans }}>{desc}</p>
              </div>
              <div style={{ padding: '8px', display: 'flex', flexDirection: 'column', gap: '6px', overflowY: 'auto', flex: 1 }}>
                {stageCards.length === 0 && <div style={{ border: `1px dashed ${color.border}`, borderRadius: '8px', padding: '20px 10px', textAlign: 'center', color: color.muted2, fontSize: '10px', fontFamily: font.mono }}>vacío</div>}
                {stageCards.map(c => <PreCard key={c.id} card={c} areas={areas} onPromote={card => { setSelectedCard(card); setShowMoveModal(true); }} onSelect={setSelectedCard} isSelected={selectedCard?.id === c.id} />)}
              </div>
            </div>
          );
        })}
      </div>

      {/* Move modal */}
      {showMoveModal && selectedCard && (
        <>
          <div style={{ position: 'fixed', inset: 0, background: '#00000080', zIndex: 300 }} onClick={() => setShowMoveModal(false)} />
          <div style={{ position: 'fixed', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', width: '320px', background: color.s1, border: `1px solid ${color.border}`, borderRadius: '12px', padding: '20px', zIndex: 301 }}>
            <p style={{ margin: '0 0 14px', fontSize: '11px', color: color.muted, fontFamily: font.mono }}>MOVER AL WORKFLOW</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
              {allStates.map(s => <button key={s.id} onClick={() => doPromote(s.id)} style={{ background: 'transparent', border: `1px solid ${color.border2}`, color: color.text, borderRadius: '8px', padding: '10px 14px', cursor: 'pointer', fontSize: '12px', fontFamily: font.sans, textAlign: 'left' }}>→ {s.name}</button>)}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
