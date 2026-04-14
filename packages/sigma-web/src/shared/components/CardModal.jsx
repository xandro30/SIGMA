import { useState, useEffect, useRef } from "react";
import { color, font, elevation, motion, radius, priority as pt, getAreaHex, BEGIN_ID, FINISH_ID } from "../tokens";
import PriorityBadge from "./PriorityBadge";
import WorkLogSection from "./tracking/WorkLogSection";

const FOCUSABLE = 'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';

export default function CardModal({ card, areas, space, spaceId, onClose, onMove, onPromote, onDemote }) {
  const [showMoveModal,   setShowMoveModal]   = useState(false);
  const [showDemoteModal, setShowDemoteModal] = useState(false);

  const modalRef = useRef(null);

  // Focus trap + Escape to close
  useEffect(() => {
    if (!card) return;
    const prev = document.activeElement;
    modalRef.current?.focus();
    const handleKey = (e) => {
      if (e.key === "Escape") { onClose(); return; }
      if (e.key === "Tab") {
        const focusable = Array.from(modalRef.current?.querySelectorAll(FOCUSABLE) ?? []);
        if (!focusable.length) return;
        const first = focusable[0];
        const last  = focusable[focusable.length - 1];
        if (e.shiftKey) {
          if (document.activeElement === first) { e.preventDefault(); last.focus(); }
        } else {
          if (document.activeElement === last)  { e.preventDefault(); first.focus(); }
        }
      }
    };
    document.addEventListener("keydown", handleKey);
    return () => { document.removeEventListener("keydown", handleKey); prev?.focus(); };
  }, [card, onClose]);

  if (!card) return null;

  const area = areas?.find((a) => a.id === card.area_id);
  const hex  = getAreaHex(area?.color_id);

  const allStates = space?.workflow_states ?? [];

  const isInWorkflow   = !!card.workflow_state_id;
  const isInBacklog    = card.pre_workflow_stage === "backlog";
  const isInWorkflowNotFinish = isInWorkflow && card.workflow_state_id !== FINISH_ID;

  const accentColor = hex || color.yellow;

  return (
    <>
      {/* Overlay */}
      <div
        aria-hidden="true"
        style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.75)", zIndex: 300, backdropFilter: "blur(8px)", animation: `fadeIn 150ms ease forwards` }}
        onClick={onClose}
      />

      {/* Modal */}
      <div
        ref={modalRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="card-modal-title"
        tabIndex={-1}
        style={{
        position:    "fixed",
        top:         "50%",
        left:        "50%",
        width:       "520px",
        maxWidth:    "94vw",
        maxHeight:   "85vh",
        background:  color.s1,
        border:      `1px solid ${color.border2}`,
        borderTop:   `3px solid ${accentColor}`,
        borderRadius: radius.lg,
        zIndex:      301,
        display:     "flex",
        flexDirection: "column",
        boxShadow:   elevation[4],
        overflow:    "hidden",
        animation:   `scaleIn 220ms cubic-bezier(0.16, 1, 0.3, 1) forwards`,
      }}>

        {/* Header */}
        <div style={{
          padding:      "14px 20px",
          borderBottom: `1px solid ${color.border}`,
          display:      "flex",
          justifyContent: "space-between",
          alignItems:   "center",
          background:   "rgba(255,255,255,0.02)",
          flexShrink:   0,
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            {area && (
              <>
                <div style={{ width: "7px", height: "7px", borderRadius: "50%", background: hex, boxShadow: `0 0 8px ${hex}90` }} />
                <span style={{ fontSize: "10px", color: hex, fontFamily: font.mono, fontWeight: 700, letterSpacing: "0.08em" }}>
                  {area.name}
                </span>
              </>
            )}
            <PriorityBadge value={card.priority} />
          </div>
          <button
            onClick={onClose}
            aria-label="Cerrar"
            style={{ background: "none", border: "none", color: color.muted, cursor: "pointer", fontSize: "18px", lineHeight: 1, padding: "2px 6px", borderRadius: radius.sm, transition: `color ${motion.fast}` }}
            onMouseEnter={e => e.currentTarget.style.color = color.text}
            onMouseLeave={e => e.currentTarget.style.color = color.muted}
          >
            ✕
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: "20px", overflowY: "auto", flex: 1 }}>

          {/* Title */}
          <h2 id="card-modal-title" style={{ margin: "0 0 10px", fontSize: "16px", color: color.text, fontFamily: font.sans, fontWeight: 700, lineHeight: "1.4" }}>
            {card.title}
          </h2>

          {/* Description */}
          {card.description && (
            <p style={{ fontSize: "12px", color: color.muted, fontFamily: font.sans, fontWeight: 400, lineHeight: "1.6", marginBottom: "18px" }}>
              {card.description}
            </p>
          )}

          {/* Estado badge */}
          <div style={{ marginBottom: "18px", display: "flex", alignItems: "center", gap: "10px" }}>
            <span style={{ fontSize: "9px", color: color.muted2, fontFamily: font.mono, letterSpacing: "0.1em", textTransform: "uppercase" }}>
              Estado
            </span>
            <span style={{
              fontSize:   "10px",
              color:      color.yellow,
              background: color.yellowDim,
              border:     `1px solid ${color.borderAccent}`,
              padding:    "3px 9px",
              borderRadius: radius.sm,
              fontFamily:  font.mono,
              fontWeight:  700,
            }}>
              {isInWorkflow
                ? allStates.find((s) => s.id === card.workflow_state_id)?.name ?? "—"
                : card.pre_workflow_stage?.toUpperCase()}
            </span>
          </div>

          {/* Action buttons */}
          <div style={{ display: "flex", gap: "8px", flexWrap: "wrap", marginBottom: "20px" }}>
            {(isInBacklog || isInWorkflowNotFinish) && (
              <ActionButton
                label={isInBacklog ? "→ Mover al Workflow" : "→ Mover estado"}
                variant="primary"
                onClick={() => setShowMoveModal(true)}
              />
            )}
            {isInWorkflow && (
              <ActionButton
                label="↩ Volver a Pre-workflow"
                variant="secondary"
                onClick={() => setShowDemoteModal(true)}
              />
            )}
          </div>

          {/* Labels */}
          {card.labels?.length > 0 && (
            <Section label="Labels">
              <div style={{ display: "flex", flexWrap: "wrap", gap: "5px" }}>
                {card.labels.map((l) => (
                  <span key={l} style={{ fontSize: "10px", color: color.muted, background: "rgba(255,255,255,0.05)", border: `1px solid ${color.border2}`, borderRadius: "4px", padding: "2px 7px", fontFamily: font.mono }}>
                    #{l}
                  </span>
                ))}
              </div>
            </Section>
          )}

          {/* Checklist */}
          {card.checklist?.length > 0 && (
            <Section label={`Checklist ${card.checklist.filter(i => i.done).length}/${card.checklist.length}`}>
              {/* Progress bar */}
              <div
                role="progressbar"
                aria-valuenow={card.checklist.filter(i => i.done).length}
                aria-valuemin={0}
                aria-valuemax={card.checklist.length}
                aria-label={`Progreso checklist: ${card.checklist.filter(i => i.done).length} de ${card.checklist.length}`}
                style={{ height: "3px", background: color.s3, borderRadius: "2px", marginBottom: "10px", overflow: "hidden" }}
              >
                <div style={{
                  height:     "100%",
                  width:      `${(card.checklist.filter(i => i.done).length / card.checklist.length) * 100}%`,
                  background: "#10B981",
                  borderRadius: "2px",
                  transition:  `width ${motion.normal}`,
                }} />
              </div>
              <ul role="list" style={{ display: "flex", flexDirection: "column", gap: "6px", listStyle: "none", margin: 0, padding: 0 }}>
                {card.checklist.map((item, i) => (
                  <li key={i} role="listitem" style={{ display: "flex", alignItems: "center", gap: "9px" }}>
                    <div
                      role="checkbox"
                      aria-checked={item.done}
                      aria-label={item.text}
                      style={{
                        width:        "12px",
                        height:       "12px",
                        borderRadius: "3px",
                        flexShrink:   0,
                        background:   item.done ? "#10B981" : "transparent",
                        border:       `1.5px solid ${item.done ? "#10B981" : color.border2}`,
                        transition:   `all ${motion.fast}`,
                      }}
                    />
                    <span aria-hidden="true" style={{
                      fontSize:       "12px",
                      color:          item.done ? color.muted2 : color.muted,
                      textDecoration: item.done ? "line-through" : "none",
                      fontFamily:     font.sans,
                      fontWeight:     400,
                    }}>
                      {item.text}
                    </span>
                  </li>
                ))}
              </ul>
            </Section>
          )}
          {/* Work log */}
          <WorkLogSection
            cardId={card.id}
            spaceId={spaceId}
            workLog={card.work_log ?? []}
          />
        </div>
      </div>

      {/* Move state modal */}
      {showMoveModal && (
        <MoveStateModal
          card={card}
          allStates={allStates}
          isFromPreWorkflow={!isInWorkflow}
          onMove={(stateId) => { if (onMove) onMove(card.id, stateId); else onPromote?.(card.id, stateId); setShowMoveModal(false); onClose(); }}
          onClose={() => setShowMoveModal(false)}
        />
      )}

      {/* Demote modal */}
      {showDemoteModal && (
        <DemoteModal
          onDemote={(stage) => { onDemote?.(card.id, stage); setShowDemoteModal(false); onClose(); }}
          onClose={() => setShowDemoteModal(false)}
        />
      )}
    </>
  );
}

function Section({ label, children }) {
  return (
    <div style={{ marginBottom: "18px" }}>
      <p style={{ margin: "0 0 8px", fontSize: "9px", color: color.muted2, fontFamily: font.mono, letterSpacing: "0.1em", textTransform: "uppercase", fontWeight: 700 }}>
        {label}
      </p>
      {children}
    </div>
  );
}

function ActionButton({ label, variant, onClick }) {
  const [hov, setHov] = useState(false);
  const isPrimary = variant === "primary";
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        background:   isPrimary ? (hov ? "rgba(245,197,24,0.22)" : color.yellowDim) : (hov ? color.s4 : color.s3),
        border:       isPrimary ? `1px solid ${color.borderAccent}` : `1px solid ${color.border2}`,
        color:        isPrimary ? color.yellow : color.muted,
        borderRadius: "8px",
        padding:      "7px 14px",
        cursor:       "pointer",
        fontSize:     "11px",
        fontFamily:   font.mono,
        fontWeight:   700,
        transition:   `all ${motion.fast}`,
      }}
    >
      {label}
    </button>
  );
}

function MoveStateModal({ card, allStates, isFromPreWorkflow, onMove, onClose }) {
  const targets  = isFromPreWorkflow
    ? allStates
    : allStates.filter((s) => s.id !== card.workflow_state_id);
  const dialogRef = useRef(null);

  useEffect(() => {
    const prev = document.activeElement;
    dialogRef.current?.focus();
    const handleKey = (e) => {
      if (e.key === "Escape") { onClose(); return; }
      if (e.key === "Tab") {
        const focusable = Array.from(dialogRef.current?.querySelectorAll(FOCUSABLE) ?? []);
        if (!focusable.length) return;
        const first = focusable[0]; const last = focusable[focusable.length - 1];
        if (e.shiftKey) { if (document.activeElement === first) { e.preventDefault(); last.focus(); } }
        else            { if (document.activeElement === last)  { e.preventDefault(); first.focus(); } }
      }
    };
    document.addEventListener("keydown", handleKey);
    return () => { document.removeEventListener("keydown", handleKey); prev?.focus(); };
  }, [onClose]);

  return (
    <>
      <div aria-hidden="true" style={{ position: "fixed", inset: 0, zIndex: 400 }} onClick={onClose} />
      <div ref={dialogRef} role="dialog" aria-modal="true" aria-label="Mover a estado" tabIndex={-1} style={{
        position:     "fixed",
        top:          "50%",
        left:         "50%",
        transform:    "translate(-50%,-50%)",
        width:        "320px",
        background:   color.s1,
        border:       `1px solid ${color.border2}`,
        borderRadius: radius.lg,
        padding:      "20px",
        zIndex:       401,
        boxShadow:    elevation[4],
        animation:    `scaleIn 180ms cubic-bezier(0.16, 1, 0.3, 1) forwards`,
      }}>
        <p style={{ margin: "0 0 14px", fontSize: "10px", color: color.muted2, fontFamily: font.mono, letterSpacing: "0.1em", textTransform: "uppercase" }}>
          Mover a
        </p>
        <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
          {targets.map((s) => (
            <MoveButton key={s.id} label={s.name} onClick={() => onMove(s.id)} />
          ))}
        </div>
      </div>
    </>
  );
}

function DemoteModal({ onDemote, onClose }) {
  const dialogRef = useRef(null);

  useEffect(() => {
    const prev = document.activeElement;
    dialogRef.current?.focus();
    const handleKey = (e) => {
      if (e.key === "Escape") { onClose(); return; }
      if (e.key === "Tab") {
        const focusable = Array.from(dialogRef.current?.querySelectorAll(FOCUSABLE) ?? []);
        if (!focusable.length) return;
        const first = focusable[0]; const last = focusable[focusable.length - 1];
        if (e.shiftKey) { if (document.activeElement === first) { e.preventDefault(); last.focus(); } }
        else            { if (document.activeElement === last)  { e.preventDefault(); first.focus(); } }
      }
    };
    document.addEventListener("keydown", handleKey);
    return () => { document.removeEventListener("keydown", handleKey); prev?.focus(); };
  }, [onClose]);

  return (
    <>
      <div aria-hidden="true" style={{ position: "fixed", inset: 0, zIndex: 400 }} onClick={onClose} />
      <div ref={dialogRef} role="dialog" aria-modal="true" aria-label="Volver a pre-workflow" tabIndex={-1} style={{
        position:     "fixed",
        top:          "50%",
        left:         "50%",
        transform:    "translate(-50%,-50%)",
        width:        "300px",
        background:   color.s1,
        border:       `1px solid ${color.border2}`,
        borderRadius: radius.lg,
        padding:      "20px",
        zIndex:       401,
        boxShadow:    elevation[4],
        animation:    `scaleIn 180ms cubic-bezier(0.16, 1, 0.3, 1) forwards`,
      }}>
        <p style={{ margin: "0 0 4px", fontSize: "10px", color: color.muted2, fontFamily: font.mono, letterSpacing: "0.1em", textTransform: "uppercase" }}>
          Volver a Pre-workflow
        </p>
        <p style={{ margin: "0 0 14px", fontSize: "11px", color: color.muted, fontFamily: font.sans, fontWeight: 400 }}>
          Inbox no está disponible una vez que la card ha salido de él.
        </p>
        <div style={{ display: "flex", flexDirection: "column", gap: "5px" }}>
          <MoveButton label="Refinement" onClick={() => onDemote("refinement")} />
          <MoveButton label="Backlog"    onClick={() => onDemote("backlog")} />
        </div>
      </div>
    </>
  );
}

function MoveButton({ label, onClick }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        background:   hov ? color.s3 : "transparent",
        border:       `1px solid ${hov ? color.border2 : color.border}`,
        color:        color.text,
        borderRadius: "8px",
        padding:      "10px 14px",
        cursor:       "pointer",
        fontSize:     "12px",
        fontFamily:   font.sans,
        fontWeight:   600,
        textAlign:    "left",
        transition:   `all ${motion.fast}`,
      }}
    >
      → {label}
    </button>
  );
}
