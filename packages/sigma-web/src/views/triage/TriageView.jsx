import { useState } from 'react';
import { color, font, getAreaHex, priority as pt, PRIORITY_ORDER } from '../../shared/tokens';
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

function TriageCard({ card, areas, isSelected, onSelect, onEdit, onMove }) {
  const area = areas.find(a => a.id === card.area_id);
  const hex  = getAreaHex(area?.color_id);
  const pr   = pt[card.priority] ?? pt.low;
  const stage = STAGES.find(s => s.id === card.pre_workflow_stage);

  return (
    <div style={{ padding: '12px', borderRadius: '9px', cursor: 'pointer', background: isSelected ? color.s3 : color.s2, border: `1px solid ${isSelected ? color.yellow : color.border}`, borderLeft: `4px solid ${pr.color}`, transition: 'all 0.12s' }}>
      {/* Click en cuerpo → seleccionar */}
      <div onClick={() => onSelect(card)}>
        <div style={{ display: 'flex', justifyContent: 'space-between', gap: '8px', marginBottom: '8px', alignItems: 'flex-start' }}>
          <p style={{ margin: 0, fontSize: '13px', color: '#fff', fontFamily: font.sans, fontWeight: 700, lineHeight: '1.4', flex: 1 }}>{card.title}</p>
          <PriorityBadge value={card.priority} />
        </div>
        {card.description && <p style={{ margin: '0 0 8px', fontSize: '11px', color: '#ccc', fontFamily: font.sans, fontWeight: 600 }}>{card.description.slice(0, 80)}{card.description.length > 80 ? '…' : ''}</p>}
        {area && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px', marginBottom: '8px' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: hex }} />
            <span style={{ fontSize: '11px', color: '#fff', fontFamily: font.mono, fontWeight: 700 }}>{area.name}</span>
          </div>
        )}
      </div>

      {/* Botones de acción */}
      <div style={{ display: 'flex', gap: '5px', borderTop: `1px solid ${color.border}`, paddingTop: '8px', flexWrap: 'wrap' }}>
        {/* Mover entre stages triage */}
        {STAGES.filter(s => s.id !== card.pre_workflow_stage).map(s => (
          <button key={s.id} onClick={e => { e.stopPropagation(); onMove('triage', card, s.id); }} style={{ background: `${s.accent}15`, border: `1px solid ${s.accent}50`, color: s.accent, borderRadius: '5px', padding: '3px 8px', cursor: 'pointer', fontSize: '10px', fontFamily: font.mono, fontWeight: 800 }}>
            → {s.label.charAt(0) + s.label.slice(1).toLowerCase()}
          </button>
        ))}
        {/* Editar */}
        <button onClick={e => { e.stopPropagation(); onEdit(card); }} style={{ background: 'transparent', border: `1px solid ${color.border2}`, color: '#fff', borderRadius: '5px', padding: '3px 8px', cursor: 'pointer', fontSize: '10px', fontFamily: font.mono, fontWeight: 700, marginLeft: 'auto' }}>
          ✏
        </button>
        {/* Mover a workflow (solo desde backlog) */}
        {card.pre_workflow_stage === 'backlog' && (
          <button onClick={e => { e.stopPropagation(); onMove('promote', card, null); }} style={{ background: color.yellow, border: 'none', color: '#000', borderRadius: '5px', padding: '3px 10px', cursor: 'pointer', fontSize: '10px', fontFamily: font.mono, fontWeight: 800 }}>
            → Workflow
          </button>
        )}
      </div>
    </div>
  );
}

export default function TriageView() {
  const activeSpaceId = useUIStore(s => s.activeSpaceId);
  const { data: spaces = [] } = useSpaces();
  const { data: cards  = [] } = useCards(activeSpaceId);
  const { data: areas  = [] } = useAreas();
  const { mutate: promoteCard      } = usePromoteCard(activeSpaceId);
  const { mutate: moveTriageStage  } = useMoveTriageStage(activeSpaceId);

  const [selected,      setSelected]      = useState(null);
  const [editCard,      setEditCard]      = useState(null);
  const [promoteTarget, setPromoteTarget] = useState(null); // card esperando elegir estado destino

  const space = spaces.find(s => s.id === activeSpaceId);
  const allStates = space?.workflow_states ?? [];
  const preCards  = cards.filter(c => c.pre_workflow_stage).sort((a, b) => (PRIORITY_ORDER[a.priority] ?? 4) - (PRIORITY_ORDER[b.priority] ?? 4));

  const handleMove = (type, card, targetId) => {
    if (type === 'triage') {
      moveTriageStage({ cardId: card.id, stage: targetId });
    } else if (type === 'promote') {
      // Abrir selector de estado destino
      setPromoteTarget(card);
    }
  };

  const handlePromote = (stateId) => {
    if (!promoteTarget) return;
    promoteCard({ cardId: promoteTarget.id, targetStateId: stateId });
    setPromoteTarget(null);
  };

  return (
    <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

      {/* Columnas */}
      <div style={{ flex: 1, display: 'flex', gap: '12px', padding: '16px', overflowX: 'auto', overflowY: 'hidden' }}>
        {STAGES.map(({ id, label, accent, desc }) => {
          const stageCards = preCards.filter(c => c.pre_workflow_stage === id);
          return (
            <div key={id} style={{ flex: 1, minWidth: '240px', background: color.s1, border: `1px solid ${color.border}`, borderTop: `4px solid ${accent}`, borderRadius: '12px', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
              <div style={{ padding: '12px 14px', borderBottom: `1px solid ${color.border}`, background: '#0d0d0d', flexShrink: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 800, color: accent, fontFamily: font.mono, letterSpacing: '0.1em' }}>{label}</span>
                  <span style={{ background: accent, color: accent === '#888888' ? '#fff' : '#000', fontSize: '12px', fontWeight: 800, padding: '2px 10px', borderRadius: '8px', fontFamily: font.mono }}>{stageCards.length}</span>
                </div>
                <p style={{ margin: 0, fontSize: '11px', color: '#aaa', fontFamily: font.sans, fontWeight: 600 }}>{desc}</p>
              </div>
              <div style={{ padding: '8px', display: 'flex', flexDirection: 'column', gap: '6px', overflowY: 'auto', flex: 1 }}>
                {stageCards.length === 0
                  ? <div style={{ border: `1px dashed ${color.border2}`, borderRadius: '8px', padding: '24px 8px', textAlign: 'center', color: '#888', fontSize: '12px', fontFamily: font.sans, fontWeight: 700 }}>vacío</div>
                  : stageCards.map(c => <TriageCard key={c.id} card={c} areas={areas} isSelected={selected?.id === c.id} onSelect={c => setSelected(prev => prev?.id === c.id ? null : c)} onEdit={setEditCard} onMove={handleMove} />)
                }
              </div>
            </div>
          );
        })}
      </div>

      {/* Panel detalle */}
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

      {/* Modal elegir estado de workflow al promover */}
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

      {editCard && <EditCardModal card={editCard} onClose={() => setEditCard(null)} />}
    </div>
  );
}
