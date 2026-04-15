import { color, font } from "../tokens";
export default function Tag({ label, onRemove }) {
  return (
    <span style={{ background:"#1a1a1a", border:`1px solid ${color.border2}`, color:color.muted,
      fontSize:"10px", padding:"2px 7px", borderRadius:"3px", letterSpacing:"0.03em",
      display:"inline-flex", alignItems:"center", gap:"4px", cursor:onRemove?"pointer":"default" }}
      onClick={onRemove}>
      #{label}
      {onRemove && <span style={{ color:color.muted, fontSize:"9px" }}>✕</span>}
    </span>
  );
}
