import { color, font, motion } from '../../tokens';
import { useCards }  from '../../../entities/card/hooks/useCards';
import { useUIStore } from '../../store/useUIStore';

const STAGES = [
  { id: 'inbox',      label: 'Inbox',      c: color.muted  },
  { id: 'refinement', label: 'Refinement', c: color.yellow },
  { id: 'backlog',    label: 'Backlog',    c: '#A78BFA'    },
];

export default function PreWorkflowSidebar() {
  const activeSpaceId = useUIStore(s => s.activeSpaceId);
  const { data: cards = [] } = useCards(activeSpaceId);
  const preCards = cards.filter(c => c.pre_workflow_stage);
  const total    = preCards.length;

  return (
    <div style={{ padding: '16px 10px' }}>
      <p style={{ fontSize: '10px', color: color.muted2, fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: '14px' }}>
        Stats pre-workflow
      </p>
      {STAGES.map(({ id, label, c }) => {
        const cnt = preCards.filter(card => card.pre_workflow_stage === id).length;
        const pct = total > 0 ? (cnt / total) * 100 : 0;
        return (
          <div key={id} style={{ marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', marginBottom: '6px' }}>
              <span style={{ fontSize: '13px', color: color.text, fontFamily: font.sans, fontWeight: 600 }}>{label}</span>
              <span style={{ fontSize: '16px', color: color.text, fontFamily: font.mono, fontWeight: 800 }}>{cnt}</span>
            </div>
            <div style={{ height: '4px', background: 'rgba(255,255,255,0.07)', borderRadius: '2px', overflow: 'hidden' }}>
              <div style={{ height: '100%', borderRadius: '2px', background: c, width: `${pct}%`, transition: `width ${motion.normal}` }} />
            </div>
          </div>
        );
      })}
      <div style={{ borderTop: `1px solid ${color.border}`, paddingTop: '14px', marginTop: '4px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '13px', color: color.muted, fontFamily: font.sans, fontWeight: 600 }}>Total en cola</span>
          <span style={{ fontSize: '20px', color: color.yellow, fontFamily: font.mono, fontWeight: 800 }}>{total}</span>
        </div>
      </div>
    </div>
  );
}
