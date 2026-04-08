import { useState } from 'react';
import { color, font, motion, radius, getAreaHex } from '../../tokens';
import { useAreas }  from '../../../entities/area/hooks/useAreas';
import { useCards }  from '../../../entities/card/hooks/useCards';
import { useSpaces } from '../../../entities/space/hooks/useSpaces';
import { useUIStore } from '../../store/useUIStore';

export default function WorkspaceSidebar() {
  const activeSpaceId    = useUIStore(s => s.activeSpaceId);
  const activeAreaFilter = useUIStore(s => s.activeAreaFilter);
  const setAreaFilter    = useUIStore(s => s.setActiveAreaFilter);
  const { data: areas  = [] } = useAreas();
  const { data: spaces = [] } = useSpaces();
  const { data: cards  = [] } = useCards(activeSpaceId);
  const space     = spaces.find(s => s.id === activeSpaceId);
  const allStates = space?.workflow_states ?? [];
  const wfCards   = cards.filter(c => c.workflow_state_id);

  const areaItems = [
    { id: 'all', name: 'Todas las áreas', hex: color.yellow },
    ...areas.map(a => ({ id: a.id, name: a.name, hex: getAreaHex(a.color_id) })),
  ];

  return (
    <div style={{ padding: '16px 10px', display: 'flex', flexDirection: 'column', gap: '24px' }}>

      {/* Area filter */}
      <SideSection label="Filtrar por área">
        {areaItems.map(({ id, name, hex }) => (
          <AreaFilterButton
            key={id}
            id={id}
            name={name}
            hex={hex}
            active={activeAreaFilter === id}
            onClick={() => setAreaFilter(id)}
          />
        ))}
      </SideSection>

      {/* Workflow counts */}
      <SideSection label="Workflow">
        {allStates.map(s => {
          const cnt = wfCards.filter(c => c.workflow_state_id === s.id).length;
          return <CountRow key={s.id} label={s.name} count={cnt} highlight={cnt > 0} />;
        })}
      </SideSection>

      {/* Pre-workflow counts */}
      <SideSection label="Pre-workflow">
        {['inbox', 'refinement', 'backlog'].map(stage => {
          const cnt = cards.filter(c => c.pre_workflow_stage === stage).length;
          return <CountRow key={stage} label={stage} count={cnt} />;
        })}
      </SideSection>
    </div>
  );
}

function SideSection({ label, children }) {
  return (
    <div>
      <p style={{ fontSize: '10px', color: color.muted2, fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', marginBottom: '8px', padding: '0 6px' }}>
        {label}
      </p>
      {children}
    </div>
  );
}

function AreaFilterButton({ id, name, hex, active, onClick }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        width:       '100%',
        textAlign:   'left',
        display:     'flex',
        alignItems:  'center',
        gap:         '8px',
        padding:     '7px 10px',
        borderRadius: radius.sm,
        marginBottom: '2px',
        border:      active ? `1px solid rgba(${hexToRgb(hex)},0.4)` : `1px solid transparent`,
        background:  active
          ? `rgba(${hexToRgb(hex)},0.14)`
          : hov ? color.s3 : 'transparent',
        color:       color.text,
        fontSize:    '12px',
        fontWeight:  active ? 700 : 500,
        fontFamily:  font.sans,
        transition:  `all ${motion.fast}`,
        cursor:      'pointer',
      }}
    >
      <div style={{
        width:        '7px',
        height:       '7px',
        borderRadius: '50%',
        background:   hex,
        flexShrink:   0,
        boxShadow:    active ? `0 0 6px ${hex}80` : 'none',
        transition:   `box-shadow ${motion.fast}`,
      }} />
      <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{name}</span>
    </button>
  );
}

function CountRow({ label, count, highlight }) {
  return (
    <div style={{
      display:        'flex',
      justifyContent: 'space-between',
      alignItems:     'center',
      padding:        '6px 10px',
      borderRadius:   radius.sm,
      background:     color.s2,
      marginBottom:   '3px',
      border:         `1px solid ${color.border}`,
    }}>
      <span style={{ fontSize: '12px', color: color.muted, fontFamily: font.sans, fontWeight: 500, textTransform: 'capitalize' }}>
        {label}
      </span>
      <span style={{ fontSize: '12px', color: highlight ? color.yellow : color.muted2, fontFamily: font.mono, fontWeight: 700 }}>
        {count}
      </span>
    </div>
  );
}

// Converts #RRGGBB to "R,G,B" for rgba() usage
function hexToRgb(hex) {
  if (!hex || !hex.startsWith('#')) return '255,255,255';
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `${r},${g},${b}`;
}
