import { color, font, layout, motion, radius, getAreaHex } from "../../../shared/tokens";
import { useUIStore } from "../../../shared/store/useUIStore";
import SectionLabel from "../../../shared/components/SectionLabel";
export default function SpaceSidebar({ space, areas }) {
  const collapsed    = useUIStore((s) => s.sidebarCollapsed);
  const toggle       = useUIStore((s) => s.toggleSidebar);
  const activeFilter = useUIStore((s) => s.activeAreaFilter);
  const toggleFilter = useUIStore((s) => s.toggleAreaFilter);
  const openCreateArea = useUIStore((s) => s.openCreateArea);
  return (
    <div style={{ width:collapsed?layout.sidebarCollapsed:layout.sidebarWidth, flexShrink:0, background:color.s1, borderRight:`1px solid ${color.border}`, display:"flex", flexDirection:"column", transition:`width ${motion.normal}`, overflow:"hidden" }}>
      <div style={{ padding:collapsed?"11px 8px":"11px 14px", borderBottom:`1px solid ${color.border}`, display:"flex", alignItems:"center", justifyContent:collapsed?"center":"space-between", flexShrink:0 }}>
        {!collapsed && <span style={{ fontSize:"9px", fontWeight:800, color:color.yellow, fontFamily:font.mono, letterSpacing:"0.1em" }}>{space?.name?.toUpperCase()??"SPACE"}</span>}
        <button onClick={toggle} style={{ background:"none", border:"none", cursor:"pointer", color:color.muted, fontSize:"14px", padding:"2px", lineHeight:1, transition:`transform ${motion.normal}`, transform:collapsed?"rotate(180deg)":"rotate(0deg)" }}>‹</button>
      </div>
      {!collapsed && (
        <div style={{ padding:"14px", overflowY:"auto", flex:1, display:"flex", flexDirection:"column", gap:"20px" }}>
          {space && (
            <div>
              <SectionLabel>Workflow</SectionLabel>
              <div style={{ display:"flex", flexDirection:"column", gap:"3px" }}>
                {[{id:"begin",name:"BEGIN",c:color.yellow},{...(space.workflow_states??[]).map((s)=>({...s,c:color.muted2}))},{id:"finish",name:"FINISH",c:"#10B981"}].flat().map((s,i)=>(
                  <div key={s.id??i} style={{ display:"flex", alignItems:"center", gap:"7px", padding:"4px 8px", borderRadius:"5px" }}>
                    <div style={{ width:"5px", height:"5px", borderRadius:"50%", background:s.c??color.muted2 }} />
                    <span style={{ fontSize:"10px", color:color.muted, fontFamily:font.mono }}>{s.name}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          <div style={{ height:"1px", background:color.border }} />
          <div>
            <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:"8px" }}>
              <SectionLabel style={{ margin:0 }}>Áreas</SectionLabel>
              <button onClick={openCreateArea} style={{ background:"none", border:"none", color:color.muted2, cursor:"pointer", fontSize:"16px", lineHeight:1, padding:0 }}>+</button>
            </div>
            <div style={{ display:"flex", flexDirection:"column", gap:"3px" }}>
              <button onClick={() => toggleFilter("all")} style={{ background:activeFilter==="all"?`${color.yellow}15`:"transparent", border:`1px solid ${activeFilter==="all"?color.yellow+"50":"transparent"}`, borderRadius:"6px", padding:"5px 9px", cursor:"pointer", display:"flex", alignItems:"center", gap:"7px", textAlign:"left" }}>
                <div style={{ width:"5px", height:"5px", borderRadius:"50%", background:activeFilter==="all"?color.yellow:color.border2 }} />
                <span style={{ fontSize:"11px", fontWeight:600, color:activeFilter==="all"?color.yellow:color.muted, fontFamily:font.sans }}>Todas</span>
              </button>
              {areas?.map((a) => {
                const hex = getAreaHex(a.color_id);
                const active = activeFilter===a.id;
                return (
                  <button key={a.id} onClick={() => toggleFilter(a.id)} style={{ background:active?`${hex}15`:"transparent", border:`1px solid ${active?hex+"50":"transparent"}`, borderRadius:"6px", padding:"5px 9px", cursor:"pointer", display:"flex", alignItems:"center", gap:"7px", textAlign:"left" }}>
                    <div style={{ width:"5px", height:"5px", borderRadius:"50%", background:active?hex:color.border2, boxShadow:active?`0 0 6px ${hex}80`:"none" }} />
                    <span style={{ fontSize:"11px", fontWeight:600, color:active?hex:color.muted, fontFamily:font.sans }}>{a.name}</span>
                  </button>
                );
              })}
              {(!areas||areas.length===0) && <p style={{ fontSize:"10px", color:color.muted2, fontFamily:font.mono, padding:"4px 9px" }}>Sin áreas</p>}
            </div>
          </div>
        </div>
      )}
      {collapsed && (
        <div style={{ padding:"10px 0", display:"flex", flexDirection:"column", alignItems:"center", gap:"8px" }}>
          {areas?.slice(0,5).map((a) => { const hex=getAreaHex(a.color_id); return <div key={a.id} style={{ width:"18px", height:"18px", borderRadius:"4px", background:`${hex}25`, border:`1px solid ${hex}60` }} />; })}
        </div>
      )}
    </div>
  );
}
