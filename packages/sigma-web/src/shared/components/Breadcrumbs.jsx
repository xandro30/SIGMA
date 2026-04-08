import { useNavigate } from "react-router-dom";
import { color, font } from "../tokens";
export default function Breadcrumbs({ items }) {
  const navigate = useNavigate();
  return (
    <div style={{ display:"flex", alignItems:"center", gap:"6px" }}>
      {items.map((item, i) => (
        <span key={i} style={{ display:"flex", alignItems:"center", gap:"6px" }}>
          {i > 0 && <span style={{ color:color.muted2, fontSize:"11px" }}>›</span>}
          {item.href
            ? <button onClick={() => navigate(item.href)} style={{ background:"none", border:"none", cursor:"pointer", padding:0, fontSize:"11px", color:color.muted, fontFamily:font.sans, fontWeight:500 }}>{item.label}</button>
            : <span style={{ fontSize:"11px", color:color.text, fontFamily:font.sans, fontWeight:600 }}>{item.label}</span>
          }
        </span>
      ))}
    </div>
  );
}
