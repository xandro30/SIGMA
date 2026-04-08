import { useState } from "react";
import { color, font, getAreaHex } from "../../../shared/tokens";
import PriorityBadge from "../../../shared/components/PriorityBadge";
const STAGES = [
  { id:"inbox",      label:"INBOX",       c:"#888888" },
  { id:"refinement", label:"REFINEMENT",  c:"#F5C518" },
  { id:"backlog",    label:"BACKLOG",      c:"#8B5CF6" },
];
function PreCard({ card, areas, onPromote }) {
  const area = areas?.find((a) => a.id===card.area_id);
  const hex  = getAreaHex(area?.color_id);
  return (
    <div style={{ padding:"8px 10px", borderRadius:"7px", background:color.s2, border:`1px solid ${color.border}`, display:"flex", alignItems:"center", gap:"8px" }}>
      <div style={{ flex:1, minWidth:0 }}>
        <p style={{ margin:0, fontSize:"11px", color:color.text, fontFamily:font.sans, fontWeight:500, overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{card.title}</p>
        {area && <div style={{ display:"flex", alignItems:"center", gap:"4px", marginTop:"3px" }}><div style={{ width:"4px", height:"4px", borderRadius:"50%", background:hex }} /><span style={{ fontSize:"9px", color:color.muted, fontFamily:font.mono }}>{area.name}</span></div>}
      </div>
      <PriorityBadge value={card.priority} />
      <button onClick={() => onPromote(card.id)} style={{ background:`${color.yellow}15`, border:`1px solid ${color.yellow}40`, color:color.yellow, borderRadius:"5px", padding:"3px 7px", cursor:"pointer", fontSize:"9px", fontFamily:font.mono, fontWeight:700, flexShrink:0 }}>→</button>
    </div>
  );
}
export default function PreWorkflowPanel({ cards, areas, onPromote }) {
  const [open, setOpen] = useState(true);
  const total = cards.length;
  if (total===0) return null;
  return (
    <div style={{ flexShrink:0, width:"220px", background:color.s1, borderRight:`1px solid ${color.border}`, display:"flex", flexDirection:"column", overflow:"hidden" }}>
      <div style={{ padding:"9px 12px", borderBottom:`1px solid ${color.border}`, display:"flex", alignItems:"center", justifyContent:"space-between", background:`rgba(255,255,255,0.02)`, cursor:"pointer" }} onClick={() => setOpen(!open)}>
        <div style={{ display:"flex", alignItems:"center", gap:"6px" }}>
          <span style={{ fontSize:"9px", fontWeight:800, color:color.muted, fontFamily:font.mono, letterSpacing:"0.1em" }}>PRE-WORKFLOW</span>
          <span style={{ background:`${color.yellow}18`, color:color.yellow, fontSize:"9px", fontWeight:700, padding:"1px 6px", borderRadius:"8px", fontFamily:font.mono }}>{total}</span>
        </div>
        <span style={{ color:color.muted2, fontSize:"10px" }}>{open?"‹":"›"}</span>
      </div>
      {open && (
        <div style={{ flex:1, overflowY:"auto", padding:"8px" }}>
          {STAGES.map(({ id, label, c }) => {
            const sc = cards.filter((x) => x.pre_workflow_stage===id);
            if (sc.length===0) return null;
            return (
              <div key={id} style={{ marginBottom:"14px" }}>
                <div style={{ display:"flex", alignItems:"center", gap:"6px", marginBottom:"6px" }}>
                  <div style={{ width:"4px", height:"4px", borderRadius:"50%", background:c }} />
                  <span style={{ fontSize:"8px", fontWeight:800, color:c, fontFamily:font.mono, letterSpacing:"0.1em" }}>{label}</span>
                  <span style={{ fontSize:"8px", color:color.muted2, fontFamily:font.mono }}>({sc.length})</span>
                </div>
                <div style={{ display:"flex", flexDirection:"column", gap:"4px" }}>
                  {sc.map((x) => <PreCard key={x.id} card={x} areas={areas} onPromote={onPromote} />)}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
