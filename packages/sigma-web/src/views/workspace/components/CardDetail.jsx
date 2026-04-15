import { color, font, layout, getAreaHex } from "../../../shared/tokens";
import PriorityBadge from "../../../shared/components/PriorityBadge";
export default function CardDetail({ card, areas, space, onClose, onMove, onArchive }) {
  const area = areas?.find((a)=>a.id===card.area_id);
  const hex  = getAreaHex(area?.color_id);
  const allStates = space?.workflow_states ?? [];
  const curName = allStates.find((s)=>s.id===card.workflow_state_id)?.name ?? card.pre_workflow_stage?.toUpperCase() ?? "—";
  return (
    <div style={{ width:"280px", flexShrink:0, background:color.s1, borderLeft:`1px solid ${color.border}`, display:"flex", flexDirection:"column", overflow:"hidden" }}>
      <div style={{ padding:"12px 14px", borderBottom:`1px solid ${color.border}`, background:"#0a0a0a", display:"flex", justifyContent:"space-between", alignItems:"center" }}>
        <div style={{ display:"flex", alignItems:"center", gap:"7px" }}>
          {area && <div style={{ width:"6px", height:"6px", borderRadius:"50%", background:hex }} />}
          <span style={{ fontSize:"10px", fontWeight:700, color:color.muted, fontFamily:font.mono, letterSpacing:"0.08em" }}>{area?.name??"Sin área"}</span>
        </div>
        <button onClick={onClose} style={{ background:"none", border:"none", color:color.muted, cursor:"pointer", fontSize:"16px", lineHeight:1 }}>✕</button>
      </div>
      <div style={{ padding:"14px", overflowY:"auto", flex:1 }}>
        <div style={{ marginBottom:"14px" }}>
          <PriorityBadge value={card.priority} size="md" />
          <h3 style={{ margin:"8px 0 0", fontSize:"13px", color:color.text, fontFamily:font.sans, fontWeight:600, lineHeight:"1.5" }}>{card.title}</h3>
        </div>
        {card.description && <p style={{ fontSize:"11px", color:color.muted, fontFamily:font.sans, lineHeight:"1.6", marginBottom:"14px" }}>{card.description}</p>}
        <div style={{ marginBottom:"14px" }}>
          <p style={{ fontSize:"9px", color:color.muted, fontFamily:font.mono, letterSpacing:"0.1em", marginBottom:"6px" }}>ESTADO</p>
          <span style={{ fontSize:"10px", color:color.yellow, fontFamily:font.mono, background:`${color.yellow}15`, border:`1px solid ${color.yellow}30`, padding:"3px 8px", borderRadius:"5px" }}>{curName}</span>
        </div>
        {card.workflow_state_id && (
          <div style={{ marginBottom:"14px" }}>
            <p style={{ fontSize:"9px", color:color.muted, fontFamily:font.mono, letterSpacing:"0.1em", marginBottom:"6px" }}>MOVER A</p>
            <div style={{ display:"flex", flexDirection:"column", gap:"4px" }}>
              {allStates.filter((s)=>s.id!==card.workflow_state_id).map((s) => (
                <button key={s.id} onClick={() => onMove(card.id,s.id)} style={{ background:"transparent", border:`1px solid ${color.border2}`, color:color.muted, borderRadius:"6px", padding:"6px 10px", cursor:"pointer", fontSize:"10px", fontFamily:font.mono, textAlign:"left" }}>→ {s.name}</button>
              ))}
            </div>
          </div>
        )}
        {card.labels?.length>0 && (
          <div style={{ marginBottom:"14px" }}>
            <p style={{ fontSize:"9px", color:color.muted, fontFamily:font.mono, letterSpacing:"0.1em", marginBottom:"6px" }}>LABELS</p>
            <div style={{ display:"flex", flexWrap:"wrap", gap:"4px" }}>
              {card.labels.map((l) => <span key={l} style={{ fontSize:"9px", color:color.muted, background:color.s2, border:`1px solid ${color.border}`, borderRadius:"3px", padding:"2px 6px", fontFamily:font.mono }}>#{l}</span>)}
            </div>
          </div>
        )}
        {card.checklist?.length>0 && (
          <div style={{ marginBottom:"14px" }}>
            <p style={{ fontSize:"9px", color:color.muted, fontFamily:font.mono, letterSpacing:"0.1em", marginBottom:"6px" }}>CHECKLIST ({card.checklist.filter((i)=>i.done).length}/{card.checklist.length})</p>
            <div style={{ display:"flex", flexDirection:"column", gap:"4px" }}>
              {card.checklist.map((item,i) => (
                <div key={i} style={{ display:"flex", alignItems:"center", gap:"7px" }}>
                  <div style={{ width:"10px", height:"10px", borderRadius:"3px", flexShrink:0, background:item.done?"#10B981":"transparent", border:`1.5px solid ${item.done?"#10B981":color.border2}` }} />
                  <span style={{ fontSize:"11px", fontFamily:font.sans, color:item.done?color.muted2:color.muted, textDecoration:item.done?"line-through":"none" }}>{item.text}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        {card.workflow_state_id && (
          <button onClick={() => onArchive(card.id)} style={{ width:"100%", background:"transparent", border:`1px solid ${color.border2}`, color:color.muted, borderRadius:"7px", padding:"8px", cursor:"pointer", fontSize:"10px", fontFamily:font.mono, marginTop:"8px" }}>📦 Archivar</button>
        )}
      </div>
    </div>
  );
}
