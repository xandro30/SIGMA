import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { color, font, elevation, motion, radius, getAreaHex } from '../../shared/tokens';
import { useAreas, useCreateArea } from '../../entities/area/hooks/useAreas';
import { useCards } from '../../entities/card/hooks/useCards';
import { useUIStore } from '../../shared/store/useUIStore';
import EditAreaModal from '../../shared/components/modals/EditAreaModal';
import SectionLabel from '../../shared/components/SectionLabel';

function AreaCard({ area, allCards, onClick, onEye }) {
  const [hov, setHov] = useState(false);
  const hex        = getAreaHex(area.color_id);
  const areaCards  = allCards.filter(c => c.area_id === area.id);
  const activeCards= areaCards.filter(c => c.workflow_state_id).length;

  return (
    <div
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        background:    color.s1,
        border:        `1px solid ${hov ? 'rgba(255,255,255,0.12)' : color.border}`,
        borderLeft:    `3px solid ${hex}`,
        borderRadius:  radius.lg,
        padding:       '18px 20px',
        display:       'flex',
        flexDirection: 'column',
        gap:           '14px',
        boxShadow:     hov ? elevation[2] : elevation[1],
        transform:     hov ? 'translateY(-2px)' : 'none',
        transition:    `all ${motion.normal}`,
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, cursor: 'pointer', minWidth: 0 }} onClick={onClick}>
          <div style={{ width: '9px', height: '9px', borderRadius: '50%', background: hex, boxShadow: `0 0 8px ${hex}60`, flexShrink: 0 }} />
          <span style={{ fontSize: '15px', fontWeight: 700, color: color.text, fontFamily: font.sans, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{area.name}</span>
        </div>
        <button onClick={e => { e.stopPropagation(); onEye(); }} title="Editar" aria-label="Editar área"
          style={{ background: 'none', border: `1px solid ${color.border2}`, borderRadius: radius.sm, color: color.muted, cursor: 'pointer', padding: '5px 10px', fontSize: '11px', fontFamily: font.mono, flexShrink: 0, marginLeft: '8px', transition: `all ${motion.fast}` }}>
          edit
        </button>
      </div>

      {area.description && (
        <p onClick={onClick} style={{ margin: 0, fontSize: '13px', color: color.muted, fontFamily: font.sans, lineHeight: '1.55', cursor: 'pointer' }}>{area.description}</p>
      )}

      {/* Stats */}
      <div onClick={onClick} style={{ display: 'flex', gap: '10px', cursor: 'pointer' }}>
        {[{ l: 'CARDS', v: areaCards.length, c: color.text }, { l: 'ACTIVAS', v: activeCards, c: hex }].map(({ l, v, c }) => (
          <div key={l} style={{ background: color.s2, border: `1px solid ${color.border}`, borderRadius: '8px', padding: '8px 12px', flex: 1, textAlign: 'center' }}>
            <div style={{ fontSize: '20px', fontWeight: 800, color: c, fontFamily: font.mono }}>{v}</div>
            <div style={{ fontSize: '10px', color: color.muted, fontFamily: font.mono, letterSpacing: '0.08em', marginTop: '2px' }}>{l}</div>
          </div>
        ))}
      </div>

      {area.objectives && (
        <p onClick={onClick} style={{ margin: 0, fontSize: '11px', color: color.muted, fontFamily: font.sans, lineHeight: '1.5', cursor: 'pointer', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
          {area.objectives}
        </p>
      )}
    </div>
  );
}

export default function AreaList() {
  const navigate      = useNavigate();
  const activeSpaceId = useUIStore(s => s.activeSpaceId);
  const { data: areas = [], isLoading } = useAreas();
  const { data: cards = [] }            = useCards(activeSpaceId);
  const { mutate: createArea }          = useCreateArea();
  const [editArea, setEditArea]         = useState(null);
  const [newName,  setNewName]          = useState('');

  return (
    <div style={{ flex: 1, overflowY: 'auto' }}>
      {/* Header */}
      <div style={{ padding: '22px 28px', borderBottom: `1px solid ${color.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '22px', fontWeight: 800, color: color.text, fontFamily: font.sans }}>Áreas</h1>
          <p style={{ margin: '4px 0 0', fontSize: '13px', color: color.muted, fontFamily: font.sans }}>Organiza tu trabajo en áreas de responsabilidad</p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <input
            value={newName}
            onChange={e => setNewName(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && newName.trim() && createArea({ name: newName.trim() }, { onSuccess: () => setNewName('') })}
            placeholder="Nueva área…"
            style={{ width: '180px', background: color.s1, border: `1.5px solid ${color.border2}`, borderRadius: '8px', color: color.text, fontSize: '13px', padding: '8px 12px', fontFamily: font.sans, outline: 'none' }}
          />
          <button
            onClick={() => newName.trim() && createArea({ name: newName.trim() }, { onSuccess: () => setNewName('') })}
            style={{ background: color.yellow, border: 'none', color: '#111', borderRadius: '8px', padding: '8px 18px', cursor: 'pointer', fontSize: '13px', fontWeight: 800, fontFamily: font.sans }}>
            + Área
          </button>
        </div>
      </div>

      {/* Grid */}
      <div style={{ padding: '24px 28px' }}>
        {isLoading
          ? <span style={{ fontSize: '13px', color: color.muted, fontFamily: font.sans }}>Cargando…</span>
          : areas.length === 0
            ? (
              <div style={{ textAlign: 'center', padding: '80px 0' }}>
                <p style={{ fontSize: '15px', color: color.muted, fontFamily: font.sans, marginBottom: '6px' }}>Sin áreas todavía</p>
                <p style={{ fontSize: '13px', color: color.muted, fontFamily: font.sans }}>Crea tu primera área con el formulario de arriba</p>
              </div>
            )
            : (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))', gap: '16px' }}>
                {areas.map(a => (
                  <AreaCard key={a.id} area={a} allCards={cards} onClick={() => navigate(`/areas/${a.id}`)} onEye={() => setEditArea(a)} />
                ))}
              </div>
            )
        }
      </div>

      {editArea && <EditAreaModal area={editArea} onClose={() => setEditArea(null)} />}
    </div>
  );
}
