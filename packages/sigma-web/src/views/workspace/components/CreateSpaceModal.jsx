import { useState } from "react";
import { color, font } from "../../../shared/tokens";
import SectionLabel from "../../../shared/components/SectionLabel";
import { useCreateSpace } from "../../../entities/space/hooks/useSpaces";
import { useUIStore } from "../../../shared/store/useUIStore";
export default function CreateSpaceModal({ onCreated }) {
  const closeModal = useUIStore((s) => s.closeCreateSpace);
  const { mutate: createSpace, isPending } = useCreateSpace();
  const [name, setName] = useState("");
  const handleCreate = () => { if(!name.trim()||isPending) return; createSpace({ name:name.trim() }, { onSuccess:(s)=>{ closeModal(); onCreated?.(s); } }); };
  return (
    <div style={{ position:"fixed", inset:0, background:"#00000095", display:"flex", alignItems:"center", justifyContent:"center", zIndex:200, backdropFilter:"blur(6px)" }}>
      <div style={{ background:color.s1, border:`1px solid ${color.border}`, borderTop:`4px solid ${color.yellow}`, borderRadius:"16px", padding:"32px", width:"400px", maxWidth:"92vw", boxShadow:"0 32px 80px #000000dd" }}>
        <style>{`input::placeholder{color:${color.muted2}}`}</style>
        <div style={{ textAlign:"center", marginBottom:"28px" }}>
          <div style={{ width:"48px", height:"48px", background:color.yellow, borderRadius:"12px", display:"flex", alignItems:"center", justifyContent:"center", fontSize:"24px", fontWeight:900, color:"#111", margin:"0 auto 14px", boxShadow:`0 0 20px ${color.yellow}50` }}>Σ</div>
          <h2 style={{ margin:"0 0 6px", fontSize:"18px", color:color.text, fontFamily:font.sans, fontWeight:800 }}>Bienvenido a SIGMA</h2>
          <p style={{ margin:0, fontSize:"12px", color:color.muted, fontFamily:font.sans }}>Crea tu primer Space para empezar</p>
        </div>
        <div style={{ marginBottom:"24px" }}>
          <SectionLabel>Nombre del Space</SectionLabel>
          <input value={name} onChange={(e)=>setName(e.target.value)} placeholder="Ej: Mi espacio de trabajo" onKeyDown={(e)=>e.key==="Enter"&&handleCreate()} autoFocus style={{ width:"100%", background:color.s2, border:`1.5px solid ${name?color.yellow:color.border2}`, borderRadius:"9px", color:color.text, fontSize:"14px", padding:"12px 14px", fontFamily:font.sans, boxSizing:"border-box" }} />
        </div>
        <button onClick={handleCreate} disabled={!name.trim()||isPending} style={{ width:"100%", background:name.trim()?color.yellow:color.s3, border:`1.5px solid ${name.trim()?color.yellow:color.border}`, color:name.trim()?"#111":color.muted2, borderRadius:"10px", padding:"13px", cursor:name.trim()?"pointer":"default", fontSize:"13px", fontWeight:800, fontFamily:font.sans, boxShadow:name.trim()?`0 0 24px ${color.yellow}40`:"none" }}>{isPending?"Creando...":"＋ Crear Space"}</button>
      </div>
    </div>
  );
}
