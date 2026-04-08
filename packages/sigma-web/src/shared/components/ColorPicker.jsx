import { areaColors } from "../tokens";
export default function ColorPicker({ selected, onSelect }) {
  return (
    <div style={{ display:"flex", flexWrap:"wrap", gap:"7px" }}>
      {areaColors.map((c) => (
        <button key={c.id} onClick={() => onSelect(c.id)} title={c.id} style={{
          width:"24px", height:"24px", borderRadius:"6px", background:c.hex, padding:0,
          border:`2px solid ${selected===c.id?"#fff":"transparent"}`,
          cursor:"pointer", flexShrink:0,
          boxShadow:selected===c.id?`0 0 8px ${c.hex}80`:"none", transition:"all 0.12s" }} />
      ))}
    </div>
  );
}
