import { color, font } from "../../../shared/tokens";
import { useUIStore } from "../../../shared/store/useUIStore";
import { useCards, useMoveCard, usePromoteCard, useArchiveCard } from "../../../entities/card/hooks/useCards";
import { useAreas } from "../../../entities/area/hooks/useAreas";
import KanbanBoard from "./KanbanBoard";
import PreWorkflowPanel from "./PreWorkflowPanel";
import CardDetail from "./CardDetail";
import { getAreaHex } from "../../../shared/tokens";
export default function SpaceView({ space }) {
  const selectedCardId  = useUIStore((s) => s.selectedCardId);
  const setSelectedCard = useUIStore((s) => s.setSelectedCardId);
  const clearSelected   = useUIStore((s) => s.clearSelectedCard);
  const activeFilter    = useUIStore((s) => s.activeAreaFilter);
  const toggleFilter    = useUIStore((s) => s.toggleAreaFilter);
  const { data:cards=[], isLoading:cardsLoading } = useCards(space?.id);
  const { data:areas=[],  isLoading:areasLoading  } = useAreas();
  const { mutate:moveCard    } = useMoveCard(space?.id);
  const { mutate:promoteCard } = usePromoteCard(space?.id);
  const { mutate:archiveCard } = useArchiveCard(space?.id);
  const selectedCard = cards.find((c)=>c.id===selectedCardId)??null;
  const handleCardClick = (card) => { if(selectedCardId===card.id) clearSelected(); else setSelectedCard(card.id); };
  const handlePromote = (cardId) => { promoteCard({cardId}); clearSelected(); };
  const handleMove    = (cardId, tsid) => { moveCard({cardId,targetStateId:tsid}); clearSelected(); };
  const handleArchive = (cardId) => { archiveCard(cardId); clearSelected(); };
  if (cardsLoading||areasLoading) return (
    <div style={{ flex:1, display:"flex", alignItems:"center", justifyContent:"center" }}>
      <span style={{ fontSize:"11px", color:color.muted, fontFamily:font.mono, letterSpacing:"0.1em" }}>Cargando…</span>
    </div>
  );
  const preCards      = cards.filter((c)=>c.pre_workflow_stage);
  const workflowCards = cards.filter((c)=>c.workflow_state_id);
  return (
    <div style={{ flex:1, display:"flex", overflow:"hidden" }}>
      {preCards.length>0 && <PreWorkflowPanel cards={preCards} areas={areas} onPromote={handlePromote} />}
      <div style={{ flex:1, display:"flex", flexDirection:"column", overflow:"hidden" }}>
        <div style={{ height:"40px", padding:"0 16px", borderBottom:`1px solid ${color.border}`, background:"#060606", display:"flex", alignItems:"center", justifyContent:"space-between", flexShrink:0 }}>
          <div style={{ display:"flex", alignItems:"center", gap:"8px" }}>
            <span style={{ fontSize:"10px", fontWeight:700, color:color.muted, fontFamily:font.mono, letterSpacing:"0.08em" }}>{space?.name?.toUpperCase()??"BOARD"}</span>
            <span style={{ fontSize:"9px", color:color.muted2, fontFamily:font.mono }}>{workflowCards.length} en workflow · {preCards.length} en cola</span>
          </div>
          <div style={{ display:"flex", gap:"4px" }}>
            <button onClick={()=>toggleFilter("all")} style={{ background:activeFilter==="all"?`${color.yellow}18`:"transparent", border:`1px solid ${activeFilter==="all"?color.yellow:color.border}`, color:activeFilter==="all"?color.yellow:color.muted, borderRadius:"5px", padding:"2px 8px", cursor:"pointer", fontSize:"9px", fontWeight:800, fontFamily:font.mono }}>ALL</button>
            {areas.map((a) => { const hex=getAreaHex(a.color_id); const act=activeFilter===a.id; return (
              <button key={a.id} onClick={()=>toggleFilter(a.id)} style={{ background:act?`${hex}22`:"transparent", border:`1px solid ${act?hex:color.border}`, color:act?hex:color.muted, borderRadius:"5px", padding:"2px 8px", cursor:"pointer", fontSize:"9px", fontWeight:800, fontFamily:font.mono }}>{a.name}</button>
            ); })}
          </div>
        </div>
        {workflowCards.length===0 ? (
          <div style={{ flex:1, display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center", gap:"12px" }}>
            <span style={{ fontSize:"32px" }}>📋</span>
            <p style={{ fontSize:"12px", color:color.muted, fontFamily:font.mono, letterSpacing:"0.08em" }}>TABLERO VACÍO</p>
            <p style={{ fontSize:"11px", color:color.muted2, fontFamily:font.sans, textAlign:"center", maxWidth:"260px", lineHeight:"1.6" }}>Crea una card y promuévela al workflow para verla aquí</p>
          </div>
        ) : (
          <KanbanBoard space={space} cards={cards} areas={areas} onCardClick={handleCardClick} />
        )}
      </div>
      {selectedCard && <CardDetail card={selectedCard} areas={areas} space={space} onClose={clearSelected} onMove={handleMove} onArchive={handleArchive} />}
    </div>
  );
}
