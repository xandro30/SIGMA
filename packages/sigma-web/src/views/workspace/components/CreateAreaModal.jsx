import { useState } from "react";
import { color, font, getAreaHex, getTextOnColor } from "../../../shared/tokens";
import SectionLabel from "../../../shared/components/SectionLabel";
import ColorPicker from "../../../shared/components/ColorPicker";
import { useCreateArea } from "../../../entities/area/hooks/useAreas";
import { useUIStore } from "../../../shared/store/useUIStore";
export default function CreateAreaModal() {
  const closeModal = useUIStore((s) => s.closeCreateArea);
  const { mutate: createArea, isPending } = useCreateArea();
  const [name, setName]       = useState("");
  const [colorId, setColorId] = useState("coral");
  const hex = getAreaHex(colorId);
  const handleCreate = () => { if(!name.trim()||isPending) return; createArea({ name:name.trim(), color_id:colorId }, { onSuccess:closeModal }); };
  return (
    <div style={{ position:"fixed", inset:0, background:"#00000095", display:"flex", alignItems:"center", justifyContent:"center", zIndex:200, backdropFilter:"blur(6px)" }} onClick={(e)=>e.target===e.currentTarget&&closeModal()}>
      <div style={{ background:color.s1, border:`1px solid ${color.border}`, borderTop:`4px solid ${hex}`, borderRadius:"16px", padding:"28px", width:"380px", maxWidth:"92vw", boxShadow:"0 32px 80px #000000dd" }}>
        <style>{`input::placeholder{color:${color.muted2}}`}</style>
        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"22px" }}>
          <div><p style={{ margin:"0 0 2px", fontSize:"9px", color:color.muted, fontFamily:font.mono, letterSpacing:"0.12em" }}>NUEVA ÁREA</p><h2 style={{ margin:0, fontSize:"15px", color:hex, fontFamily:font.mono, fontWeight:800 }}>Σ SIGMA</h2></div>
          <button onClick={closeModal} style={{ background:"none", border:"none", color:color.muted, cursor:"pointer", fontSize:"18px" }}>✕</button>
        </div>
        <div style={{ marginBottom:"18px" }}>
          <SectionLabel>Nombre *</SectionLabel>
          <input value={name} onChange={(e)=>setName(e.target.value)} placeholder="Ej: Work, Personal, Fitness..." style={{ width:"100%", background:color.s2, border:`1.5px solid ${name?hex:color.border2}`, borderRadius:"9px", color:color.text, fontSize:"13px", padding:"11px 13px", fontFamily:font.sans, boxSizing:"border-box" }} />
        </div>
        <div style={{ marginBottom:"24px" }}><SectionLabel>Color</SectionLabel><ColorPicker selected={colorId} onSelect={setColorId} /></div>
        <div style={{ display:"flex", gap:"10px", justifyContent:"flex-end" }}>
          <button onClick={closeModal} style={{ background:"transparent", border:`1px solid ${color.border2}`, color:color.muted, borderRadius:"8px", padding:"10px 18px", cursor:"pointer", fontSize:"12px", fontFamily:font.sans }}>Cancelar</button>
          <button onClick={handleCreate} disabled={!name.trim()||isPending} style={{ background:name.trim()?hex:color.s3, border:`1.5px solid ${name.trim()?hex:color.border}`, color:name.trim()?getTextOnColor(hex):color.muted2, borderRadius:"8px", padding:"10px 22px", cursor:name.trim()?"pointer":"default", fontSize:"12px", fontWeight:800, fontFamily:font.sans }}>{isPending?"Creando...":"＋ Crear área"}</button>
        </div>
      </div>
    </div>
  );
}
