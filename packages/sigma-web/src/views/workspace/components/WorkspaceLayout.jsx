import { color, font } from '../../../shared/tokens';
import { useUIStore } from '../../../shared/store/useUIStore';
import { useSpaces } from '../../../entities/space/hooks/useSpaces';
import { useCards } from '../../../entities/card/hooks/useCards';
import { useAreas } from '../../../entities/area/hooks/useAreas';
import KanbanBoard from './KanbanBoard';
import { WS } from '../../../shared/workStates';
import { FINISH_ID } from '../../../shared/tokens';

export default function WorkspaceLayout() {
  const activeSpaceId = useUIStore(s => s.activeSpaceId);
  const { data: spaces = [] } = useSpaces();
  const { data: cards  = [], isLoading } = useCards(activeSpaceId);
  const { data: areas  = [] } = useAreas();
  const space = spaces.find(s => s.id === activeSpaceId);

  const wfCards    = cards.filter(c => c.workflow_state_id);
  const inProgress = wfCards.filter(c => c.workflow_state_id !== FINISH_ID).length;
  const done       = wfCards.filter(c => c.workflow_state_id === FINISH_ID).length;

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden' }}>
      {/* Sub-header */}
      <div style={{ padding:'10px 18px', borderBottom:`1px solid ${color.border}`, flexShrink:0, background:'#090909', display:'flex', alignItems:'center', gap:'16px' }}>
        <span style={{ fontSize:'14px', fontWeight:800, color:'#fff', fontFamily:font.sans }}>{space?.name ?? '—'}</span>
        <div style={{ width:'1px', height:'16px', background:color.border2 }} />
        <div style={{ display:'flex', gap:'12px' }}>
          {[
            { label:'En progreso', v:inProgress, c:WS.active.color },
            { label:'Completadas', v:done,        c:WS.done.color   },
            { label:'Total',       v:wfCards.length, c:'#fff'       },
          ].map(({ label, v, c }) => (
            <div key={label} style={{ display:'flex', alignItems:'center', gap:'5px' }}>
              <span style={{ fontSize:'15px', fontWeight:800, color:c, fontFamily:font.mono }}>{v}</span>
              <span style={{ fontSize:'11px', fontWeight:700, color:'#aaa', fontFamily:font.sans }}>{label}</span>
            </div>
          ))}
        </div>
        {isLoading && <span style={{ fontSize:'11px', color:'#888', fontFamily:font.mono, marginLeft:'auto' }}>Cargando…</span>}
      </div>
      <KanbanBoard space={space} cards={cards} areas={areas} />
    </div>
  );
}
