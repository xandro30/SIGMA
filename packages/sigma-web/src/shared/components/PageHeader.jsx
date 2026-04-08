import { color, font } from "../tokens";
import Breadcrumbs from "./Breadcrumbs";
export default function PageHeader({ breadcrumbs, title, subtitle, actions, colorAccent }) {
  return (
    <div style={{ padding:"20px 24px 0", flexShrink:0 }}>
      {breadcrumbs && <div style={{ marginBottom:"12px" }}><Breadcrumbs items={breadcrumbs} /></div>}
      <div style={{ display:"flex", alignItems:"flex-start", justifyContent:"space-between", marginBottom:"20px" }}>
        <div>
          {colorAccent && <div style={{ width:"3px", height:"32px", background:colorAccent, borderRadius:"2px", display:"inline-block", marginRight:"12px", verticalAlign:"middle" }} />}
          <span style={{ fontSize:"20px", fontWeight:800, color:color.text, fontFamily:font.sans }}>{title}</span>
          {subtitle && <p style={{ margin:"4px 0 0", fontSize:"12px", color:color.muted, fontFamily:font.sans }}>{subtitle}</p>}
        </div>
        {actions && <div style={{ display:"flex", gap:"8px" }}>{actions}</div>}
      </div>
    </div>
  );
}
