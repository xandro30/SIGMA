import { color, font } from '../../tokens';
import { useCards } from '../../../entities/card/hooks/useCards';
import { useUIStore } from '../../store/useUIStore';

const STAGES = [
  { id:'inbox',      label:'Inbox',      accent:'#999999' },
  { id:'refinement', label:'Refinement', accent:'#F5C518' },
  { id:'backlog',    label:'Backlog',    accent:'#8B5CF6' },
];

export default function TriageSidebar() {
  const activeSpaceId = useUIStore(s => s.activeSpaceId);
  const { data: cards = [] } = useCards(activeSpaceId);
  const preCards = cards.filter(c => c.pre_workflow_stage);
  const total    = preCards.length;

  return (
    <div style={{ padding:'16px 12px' }}>
      <p style={{ margin:'0 0 16px', fontSize:'11px', color:'#fff', fontFamily:font.mono, fontWeight:700, letterSpacing:'0.12em', textTransform:'uppercase' }}>Triage</p>

      {STAGES.map(({ id, label, accent }) => {
        const cnt = preCards.filter(c => c.pre_workflow_stage === id).length;
        const pct = total > 0 ? Math.round((cnt/total)*100) : 0;
        return (
          <div key={id} style={{ marginBottom:'16px' }}>
            <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'6px' }}>
              <span style={{ fontSize:'13px', color:'#fff', fontFamily:font.sans, fontWeight:700 }}>{label}</span>
              <span style={{ fontSize:'16px', color:accent, fontFamily:font.mono, fontWeight:800 }}>{cnt}</span>
            </div>
            <div style={{ height:'6px', background:color.border2, borderRadius:'3px' }}>
              <div style={{ height:'100%', borderRadius:'3px', background:accent, width:`${pct}%`, transition:'width 0.3s' }} />
            </div>
          </div>
        );
      })}

      <div style={{ borderTop:`1px solid ${color.border2}`, paddingTop:'14px', marginTop:'4px', display:'flex', justifyContent:'space-between', alignItems:'center' }}>
        <span style={{ fontSize:'13px', color:'#fff', fontFamily:font.sans, fontWeight:700 }}>Total en cola</span>
        <span style={{ fontSize:'22px', color:color.yellow, fontFamily:font.mono, fontWeight:800 }}>{total}</span>
      </div>
    </div>
  );
}
