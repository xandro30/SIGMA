import { useNavigate } from 'react-router-dom';
import { color, font, getAreaHex } from '../tokens';
import { WS, seededRandom, mockCardCounts } from '../workStates';

// ── Mini badge de estado ──────────────────────────────────────────────────────
function StatBadge({ ws, count }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', background: ws.bg, border: `1px solid ${ws.color}50`, borderRadius: '6px', padding: '4px 8px', flexShrink: 0 }}>
      <span style={{ fontSize: '11px', color: ws.color, fontFamily: font.mono, fontWeight: 800 }}>{ws.icon}</span>
      <span style={{ fontSize: '13px', color: ws.color, fontFamily: font.mono, fontWeight: 800 }}>{count}</span>
    </div>
  );
}

// ── Barra de progreso con % ───────────────────────────────────────────────────
function ProgressBar({ pct, colorHex, label }) {
  return (
    <div>
      {label && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '5px' }}>
          <span style={{ fontSize: '12px', color: '#FFFFFF', fontFamily: font.sans, fontWeight: 600 }}>▸ {label}</span>
          <span style={{ fontSize: '12px', color: colorHex, fontFamily: font.mono, fontWeight: 800 }}>{pct}%</span>
        </div>
      )}
      <div style={{ height: '6px', background: color.border2, borderRadius: '3px', overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${pct}%`, background: colorHex, borderRadius: '3px', transition: 'width 0.4s ease' }} />
      </div>
    </div>
  );
}

// ── Fila de épica ─────────────────────────────────────────────────────────────
function EpicRow({ epic }) {
  const counts = mockCardCounts(epic.id);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '8px 0', borderBottom: `1px solid ${color.border}` }}>
      <span style={{ fontSize: '13px', color: '#FFFFFF', fontFamily: font.sans, fontWeight: 700, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {epic.name}
      </span>
      <div style={{ display: 'flex', gap: '6px', flexShrink: 0 }}>
        <StatBadge ws={WS.active}  count={counts.active}  />
        <StatBadge ws={WS.waiting} count={counts.waiting} />
        <StatBadge ws={WS.done}    count={counts.done}    />
        <StatBadge ws={WS.total}   count={counts.total}   />
      </div>
    </div>
  );
}

// ── SummaryBlock principal ────────────────────────────────────────────────────
export default function SummaryBlock({ type = 'project', data, epics = [], areaId, hex, navigateTo }) {
  const navigate = useNavigate();
  const accentHex = hex ?? getAreaHex(data?.color_id);

  // Progreso global (seeded, no cambia entre renders)
  const globalPct = seededRandom(data.id + 'global');

  // Progreso por objetivo (seeded por objetivo + id)
  const objectives = data?.objectives ?? [];

  return (
    <div style={{
      background: color.s1,
      border: `1px solid ${color.border}`,
      borderLeft: `4px solid ${accentHex}`,
      borderRadius: '12px',
      overflow: 'hidden',
    }}>

      {/* ── Header ── */}
      <div style={{ padding: '16px 18px', borderBottom: `1px solid ${color.border}`, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', background: '#0e0e0e' }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
            <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: accentHex, boxShadow: `0 0 8px ${accentHex}80`, flexShrink: 0 }} />
            <h3 style={{ margin: 0, fontSize: '15px', fontWeight: 800, color: '#FFFFFF', fontFamily: font.sans, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {data.name}
            </h3>
          </div>
          {data.description && (
            <p style={{ margin: 0, fontSize: '12px', color: '#FFFFFF', fontFamily: font.sans, fontWeight: 600, lineHeight: '1.5', paddingLeft: '16px' }}>
              {data.description}
            </p>
          )}
        </div>
        {navigateTo && (
          <button
            onClick={() => navigate(navigateTo)}
            style={{ background: accentHex, border: 'none', borderRadius: '7px', color: '#000000', fontSize: '12px', fontWeight: 800, padding: '6px 12px', cursor: 'pointer', fontFamily: font.sans, flexShrink: 0, marginLeft: '12px' }}>
            Abrir →
          </button>
        )}
      </div>

      <div style={{ padding: '16px 18px', display: 'flex', flexDirection: 'column', gap: '16px' }}>

        {/* ── Progreso global ── */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '7px' }}>
            <span style={{ fontSize: '10px', color: '#FFFFFF', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Progreso general</span>
            <span style={{ fontSize: '14px', color: WS.done.color, fontFamily: font.mono, fontWeight: 800 }}>{globalPct}%</span>
          </div>
          <div style={{ height: '8px', background: color.border2, borderRadius: '4px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${globalPct}%`, background: `linear-gradient(90deg, ${WS.active.color}, ${WS.done.color})`, borderRadius: '4px', transition: 'width 0.5s ease' }} />
          </div>
        </div>

        {/* ── Objetivos (solo en projects) ── */}
        {type === 'project' && objectives.length > 0 && (
          <div>
            <p style={{ margin: '0 0 10px', fontSize: '10px', color: '#FFFFFF', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Objetivos</p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {objectives.map((obj, i) => {
                const pct = seededRandom(data.id + obj + i);
                return <ProgressBar key={i} pct={pct} colorHex={accentHex} label={obj} />;
              })}
            </div>
          </div>
        )}

        {/* ── Épicas ── */}
        {epics.length > 0 && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <p style={{ margin: 0, fontSize: '10px', color: '#FFFFFF', fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Épicas</p>
              {/* Leyenda */}
              <div style={{ display: 'flex', gap: '8px' }}>
                {Object.values(WS).map(ws => (
                  <div key={ws.label} style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                    <span style={{ fontSize: '10px', color: ws.color, fontFamily: font.mono, fontWeight: 800 }}>{ws.icon}</span>
                    <span style={{ fontSize: '9px', color: ws.color, fontFamily: font.mono, fontWeight: 700 }}>{ws.label.split(' ')[0]}</span>
                  </div>
                ))}
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {epics.map(e => <EpicRow key={e.id} epic={e} />)}
            </div>
          </div>
        )}

        {/* ── Sin épicas placeholder ── */}
        {epics.length === 0 && type === 'project' && (
          <div style={{ border: `1px dashed ${color.border2}`, borderRadius: '8px', padding: '14px', textAlign: 'center' }}>
            <p style={{ margin: 0, fontSize: '12px', color: '#FFFFFF', fontFamily: font.sans, fontWeight: 600 }}>Sin épicas definidas</p>
          </div>
        )}

      </div>
    </div>
  );
}
