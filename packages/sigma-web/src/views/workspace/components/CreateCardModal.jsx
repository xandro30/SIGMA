import { useState } from "react";
import { color, font, priority as pt, getAreaHex } from "../../../shared/tokens";
import SectionLabel from "../../../shared/components/SectionLabel";
import { useCreateCard } from "../../../entities/card/hooks/useCards";
import { useUIStore } from "../../../shared/store/useUIStore";
const STAGES = [
  { id:"inbox",      label:"📥 Inbox"      },
  { id:"refinement", label:"🔍 Refinement"  },
  { id:"backlog",    label:"📦 Backlog"     },
];
export default function CreateCardModal({ spaceId, areas }) {
  const closeModal = useUIStore((s) => s.closeCreateCard);
  const { mutate: createCard, isPending } = useCreateCard(spaceId);
  const [title, setTitle]   = useState("");
  const [priority, setPri]  = useState("medium");
  const [areaId, setAreaId] = useState(areas?.[0]?.id ?? "");
  const [stage, setStage]   = useState("inbox");
  const [li, setLi]         = useState("");
  const [labels, setLabels] = useState([]);
  const areaColor = getAreaHex(areas?.find((a)=>a.id===areaId)?.color_id);
  const addLabel = () => { const t=li.trim().toLowerCase().replace(/\s+/g,"-"); if(t&&!labels.includes(t)) setLabels([...labels,t]); setLi(""); };
  const handleCreate = () => { if(!title.trim()||isPending) return; createCard({ title:title.trim(), priority, area_id:areaId||null, initial_stage:stage, labels }, { onSuccess:closeModal }); };
  return (
    <div style={{ position:"fixed", inset:0, background:"#00000095", display:"flex", alignItems:"center", justifyContent:"center", zIndex:200, backdropFilter:"blur(6px)" }} onClick={(e)=>e.target===e.currentTarget&&closeModal()}>
      <div style={{ background:color.s1, border:`1px solid ${color.border}`, borderTop:`4px solid ${areaColor}`, borderRadius:"16px", padding:"28px", width:"440px", maxWidth:"92vw", maxHeight:"90vh", overflowY:"auto", boxShadow:"0 32px 80px #000000dd" }}>
        <style>{`textarea::placeholder,input::placeholder{color:${color.muted2}}`}</style>
        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"22px" }}>
          <div><p style={{ margin:"0 0 2px", fontSize:"9px", color:color.muted, fontFamily:font.mono, letterSpacing:"0.12em" }}>NUEVA CARD</p><h2 style={{ margin:0, fontSize:"15px", color:color.yellow, fontFamily:font.mono, fontWeight:800 }}>Σ SIGMA</h2></div>
          <button onClick={closeModal} style={{ background:"none", border:"none", color:color.muted, cursor:"pointer", fontSize:"18px" }}>✕</button>
        </div>
        <div style={{ marginBottom:"18px" }}>
          <SectionLabel>Título *</SectionLabel>
          <textarea value={title} onChange={(e)=>setTitle(e.target.value)} placeholder="¿Qué tienes que hacer?" rows={2} style={{ width:"100%", background:color.s2, border:`1.5px solid ${title?areaColor:color.border2}`, borderRadius:"9px", color:color.text, fontSize:"13px", padding:"11px 13px", fontFamily:font.sans, resize:"none", boxSizing:"border-box", lineHeight:"1.5" }} />
        </div>
        {areas?.length>0 && (
          <div style={{ marginBottom:"18px" }}>
            <SectionLabel>Área</SectionLabel>
            <div style={{ display:"flex", gap:"6px", flexWrap:"wrap" }}>
              <button onClick={()=>setAreaId("")} style={{ background:!areaId?`${color.yellow}20`:"transparent", border:`1.5px solid ${!areaId?color.yellow:color.border2}`, color:!areaId?color.yellow:color.muted, borderRadius:"7px", padding:"5px 10px", cursor:"pointer", fontSize:"10px", fontWeight:700, fontFamily:font.mono }}>Sin área</button>
              {areas.map((a) => { const hex=getAreaHex(a.color_id); const act=areaId===a.id; return (
                <button key={a.id} onClick={()=>setAreaId(a.id)} style={{ background:act?`${hex}22`:"transparent", border:`1.5px solid ${act?hex:color.border2}`, color:act?hex:color.muted, borderRadius:"7px", padding:"5px 10px", cursor:"pointer", fontSize:"10px", fontWeight:700, fontFamily:font.mono, display:"flex", alignItems:"center", gap:"5px" }}>
                  <span style={{ width:"6px", height:"6px", borderRadius:"50%", background:hex }} />{a.name}
                </button>
              ); })}
            </div>
          </div>
        )}
        <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"14px", marginBottom:"18px" }}>
          <div>
            <SectionLabel>Etapa inicial</SectionLabel>
            <div style={{ display:"flex", flexDirection:"column", gap:"4px" }}>
              {STAGES.map((s) => <button key={s.id} onClick={()=>setStage(s.id)} style={{ background:stage===s.id?`${color.yellow}15`:"transparent", border:`1.5px solid ${stage===s.id?color.yellow+"50":color.border2}`, color:stage===s.id?color.yellow:color.muted, borderRadius:"6px", padding:"5px 8px", cursor:"pointer", fontSize:"10px", fontFamily:font.mono, textAlign:"left" }}>{s.label}</button>)}
            </div>
          </div>
          <div>
            <SectionLabel>Prioridad</SectionLabel>
            <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:"5px" }}>
              {Object.entries(pt).map(([key,p]) => <button key={key} onClick={()=>setPri(key)} style={{ background:priority===key?p.bg:"transparent", border:`1.5px solid ${priority===key?p.color:color.border2}`, color:priority===key?p.color:color.muted, borderRadius:"6px", padding:"6px 0", cursor:"pointer", fontSize:"9px", fontWeight:800, letterSpacing:"0.08em", fontFamily:font.mono }}>{p.label}</button>)}
            </div>
          </div>
        </div>
        <div style={{ marginBottom:"24px" }}>
          <SectionLabel>Labels</SectionLabel>
          <div style={{ display:"flex", gap:"7px", marginBottom:"8px" }}>
            <input value={li} onChange={(e)=>setLi(e.target.value)} onKeyDown={(e)=>e.key==="Enter"&&addLabel()} placeholder="ej: GCP… Enter para añadir" style={{ flex:1, background:color.s2, border:`1.5px solid ${color.border2}`, borderRadius:"8px", color:color.text, fontSize:"12px", padding:"8px 12px", fontFamily:font.mono }} />
            <button onClick={addLabel} style={{ background:`${areaColor}22`, border:`1.5px solid ${areaColor}`, color:areaColor, borderRadius:"8px", padding:"8px 14px", cursor:"pointer", fontSize:"14px", fontWeight:700 }}>+</button>
          </div>
          <div style={{ display:"flex", flexWrap:"wrap", gap:"5px", minHeight:"22px" }}>
            {labels.length===0?<span style={{ fontSize:"10px", color:color.muted2, fontFamily:font.mono }}>Sin labels</span>:labels.map((t)=><span key={t} style={{ fontSize:"9px", color:color.muted, background:color.s2, border:`1px solid ${color.border}`, borderRadius:"3px", padding:"2px 6px", fontFamily:font.mono, cursor:"pointer" }} onClick={()=>setLabels(labels.filter((x)=>x!==t))}>#{t} ✕</span>)}
          </div>
        </div>
        <div style={{ display:"flex", gap:"10px", justifyContent:"flex-end" }}>
          <button onClick={closeModal} style={{ background:"transparent", border:`1px solid ${color.border2}`, color:color.muted, borderRadius:"8px", padding:"10px 18px", cursor:"pointer", fontSize:"12px", fontFamily:font.sans }}>Cancelar</button>
          <button onClick={handleCreate} disabled={!title.trim()||isPending} style={{ background:title.trim()?color.yellow:color.s3, border:`1.5px solid ${title.trim()?color.yellow:color.border}`, color:title.trim()?"#111":color.muted2, borderRadius:"8px", padding:"10px 22px", cursor:title.trim()?"pointer":"default", fontSize:"12px", fontWeight:800, fontFamily:font.sans, boxShadow:title.trim()?`0 0 20px ${color.yellow}40`:"none" }}>{isPending?"Creando...":"＋ Crear card"}</button>
        </div>
      </div>
    </div>
  );
}
