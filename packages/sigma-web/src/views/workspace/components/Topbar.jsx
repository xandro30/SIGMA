import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { color, font, elevation, motion, radius } from '../../../shared/tokens';
import { useUIStore }  from '../../../shared/store/useUIStore';
import { useSpaces }   from '../../../entities/space/hooks/useSpaces';
import { useEscapeKey } from '../../../shared/hooks/useEscapeKey';

// SVG-based nav icons (no emojis — consistent stroke weight, themeable)
const ICONS = {
  board:      () => <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><rect x="1" y="1" width="5" height="14" rx="1.5"/><rect x="10" y="1" width="5" height="9" rx="1.5"/><rect x="10" y="12" width="5" height="3" rx="1.5"/></svg>,
  triage:     () => <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M8 1v14M3 5l5-4 5 4"/><path d="M4 9h8"/></svg>,
  areas:      () => <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><rect x="1" y="1" width="6" height="6" rx="1.5"/><rect x="9" y="1" width="6" height="6" rx="1.5"/><rect x="1" y="9" width="6" height="6" rx="1.5"/><rect x="9" y="9" width="6" height="6" rx="1.5"/></svg>,
  scheduling: () => <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><rect x="1" y="3" width="14" height="12" rx="2"/><path d="M5 1v4M11 1v4M1 7h14"/></svg>,
  metrics:    () => <svg width="14" height="14" viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"><path d="M1 13l4-5 3 2 3-6 4 3"/></svg>,
};

const NAV_ITEMS = [
  { id: 'board',      path: '/workspace',  label: 'Board',    available: true },
  { id: 'triage',     path: '/triage',     label: 'Triage',   available: true },
  { id: 'areas',      path: '/areas',      label: 'Áreas',    available: true },
  { id: 'scheduling', path: '/scheduling', label: 'Schedule', available: true },
  { id: 'metrics',    path: '/metrics',    label: 'Metrics',  available: true },
];

function NavItem({ item, isActive, onClick }) {
  const [hov, setHov] = useState(false);
  const Icon = ICONS[item.id];

  if (!item.available) return (
    <div
      title="Próximamente"
      style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 14px', borderRadius: radius.sm, opacity: 0.28, cursor: 'not-allowed', color: color.text, fontSize: '12px', fontFamily: font.sans, fontWeight: 600 }}
    >
      <Icon /><span>{item.label}</span>
    </div>
  );

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        display:     'flex',
        alignItems:  'center',
        gap:         '6px',
        padding:     '6px 14px',
        borderRadius: radius.sm,
        border:      'none',
        background:  isActive
          ? color.yellow
          : hov ? 'rgba(255,255,255,0.08)' : 'transparent',
        color:       isActive ? '#000' : color.text,
        fontSize:    '12px',
        fontWeight:  isActive ? 800 : 600,
        fontFamily:  font.sans,
        boxShadow:   isActive ? `0 0 14px ${color.yellow}40` : 'none',
        transition:  `all ${motion.fast}`,
        cursor:      'pointer',
      }}
    >
      <Icon />
      <span>{item.label}</span>
    </button>
  );
}

export default function Topbar() {
  const navigate         = useNavigate();
  const { pathname }     = useLocation();
  const activeSpaceId    = useUIStore(s => s.activeSpaceId);
  const setActiveSpaceId = useUIStore(s => s.setActiveSpaceId);
  const openCreateCard   = useUIStore(s => s.openCreateCard);
  const { data: spaces = [] } = useSpaces();
  const [dropOpen, setDropOpen] = useState(false);
  const [dropHov,  setDropHov]  = useState(false);
  const closeDrop = useCallback(() => setDropOpen(false), []);
  useEscapeKey(dropOpen ? closeDrop : null);

  // Auto-select first space when activeSpaceId is null or no longer exists in Firestore
  useEffect(() => {
    if (!spaces.length) return;
    const exists = spaces.some(s => s.id === activeSpaceId);
    if (!exists) setActiveSpaceId(spaces[0].id);
  }, [spaces, activeSpaceId, setActiveSpaceId]);

  const activeSpace = spaces.find(s => s.id === activeSpaceId);
  const activeNavId = (() => {
    if (pathname.startsWith('/triage'))     return 'triage';
    if (pathname.startsWith('/workspace'))  return 'board';
    if (pathname.startsWith('/areas'))      return 'areas';
    if (pathname.startsWith('/scheduling')) return 'scheduling';
    if (pathname.startsWith('/metrics'))    return 'metrics';
    return 'board';
  })();

  return (
    <header style={{
      height:      '56px',
      background:  'rgba(6,6,6,0.85)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      borderBottom: `1px solid ${color.border}`,
      display:     'flex',
      alignItems:  'center',
      padding:     '0 20px',
      flexShrink:  0,
      position:    'sticky',
      top:         0,
      zIndex:      100,
    }}>

      {/* LEFT — brand + space selector */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexShrink: 0, minWidth: '220px' }}>

        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexShrink: 0 }}>
          <div style={{
            background:   color.yellow,
            width:        '30px',
            height:       '30px',
            borderRadius: radius.sm,
            display:      'flex',
            alignItems:   'center',
            justifyContent: 'center',
            fontSize:     '15px',
            fontWeight:   900,
            color:        '#000',
            boxShadow:    `0 0 14px ${color.yellow}50`,
            flexShrink:   0,
          }}>Σ</div>
          <span style={{ fontSize: '14px', fontWeight: 800, color: color.yellow, fontFamily: font.mono, letterSpacing: '0.1em' }}>SIGMA</span>
        </div>

        <div style={{ width: '1px', height: '20px', background: color.border, flexShrink: 0 }} />

        {/* Space selector */}
        <div style={{ position: 'relative', flexShrink: 0 }}>
          <button
            onClick={() => setDropOpen(o => !o)}
            onMouseEnter={() => setDropHov(true)}
            onMouseLeave={() => setDropHov(false)}
            style={{
              display:     'flex',
              alignItems:  'center',
              gap:         '7px',
              padding:     '5px 11px 5px 12px',
              background:  color.s2,
              border:      `1px solid ${dropOpen || dropHov ? color.border2 : color.border}`,
              borderRadius: radius.md,
              cursor:      'pointer',
              transition:  `all ${motion.fast}`,
              boxShadow:   dropOpen ? elevation[2] : 'none',
            }}
          >
            <span style={{ fontSize: '13px', fontWeight: 700, color: color.text, fontFamily: font.sans, whiteSpace: 'nowrap' }}>
              {activeSpace?.name ?? 'Sin space'}
            </span>
            <span style={{ fontSize: '10px', color: color.muted, fontWeight: 600, display: 'inline-block', transform: dropOpen ? 'rotate(180deg)' : 'none', transition: `transform ${motion.fast}` }}>▼</span>
          </button>

          {dropOpen && (
            <>
              <div style={{ position: 'fixed', inset: 0, zIndex: 200 }} onClick={() => setDropOpen(false)} />
              <div style={{
                position:     'absolute',
                top:          'calc(100% + 6px)',
                left:         0,
                background:   color.s2,
                border:       `1px solid ${color.border2}`,
                borderRadius: radius.lg,
                padding:      '8px',
                minWidth:     '200px',
                zIndex:       201,
                boxShadow:    elevation[3],
                animation:    `slideInUp 180ms cubic-bezier(0.16, 1, 0.3, 1) forwards`,
              }}>
                <p style={{ margin: '0 0 6px', padding: '2px 8px', fontSize: '9px', color: color.muted, fontFamily: font.mono, fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase' }}>
                  Spaces
                </p>
                {spaces.map(s => (
                  <SpaceDropItem
                    key={s.id}
                    space={s}
                    active={s.id === activeSpaceId}
                    onClick={() => { setActiveSpaceId(s.id); setDropOpen(false); }}
                  />
                ))}
                <div style={{ height: '1px', background: color.border, margin: '6px 0' }} />
                <DropAction
                  label="Configurar spaces"
                  onClick={() => { navigate(`/spaces/${activeSpaceId}/settings`); setDropOpen(false); }}
                />
              </div>
            </>
          )}
        </div>
      </div>

      {/* CENTER — navigation */}
      <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
        <nav
          aria-label="Navegación principal"
          style={{ display: 'flex', alignItems: 'center', gap: '2px', background: color.s2, border: `1px solid ${color.border}`, borderRadius: radius.lg, padding: '4px' }}
        >
          {NAV_ITEMS.map(item => (
            <NavItem
              key={item.id}
              item={item}
              isActive={item.id === activeNavId}
              onClick={() => item.available && navigate(item.path)}
            />
          ))}
        </nav>
      </div>

      {/* RIGHT — create card */}
      <div style={{ display: 'flex', alignItems: 'center', minWidth: '120px', justifyContent: 'flex-end' }}>
        <CreateCardButton onClick={openCreateCard} />
      </div>
    </header>
  );
}

function SpaceDropItem({ space, active, onClick }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        width:       '100%',
        display:     'flex',
        alignItems:  'center',
        gap:         '8px',
        background:  active ? color.yellowDim : hov ? color.s3 : 'transparent',
        border:      `1px solid ${active ? color.borderAccent : 'transparent'}`,
        borderRadius: '8px',
        padding:     '8px 12px',
        cursor:      'pointer',
        fontSize:    '13px',
        fontFamily:  font.sans,
        fontWeight:  active ? 700 : 500,
        marginBottom: '2px',
        color:       active ? color.yellow : color.text,
        transition:  `all ${motion.fast}`,
      }}
    >
      {active && <span style={{ fontSize: '10px', color: color.yellow }}>✓</span>}
      {space.name}
    </button>
  );
}

function DropAction({ label, onClick }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        width:       '100%',
        background:  hov ? color.s3 : 'transparent',
        border:      'none',
        color:       color.muted,
        borderRadius: '8px',
        padding:     '7px 12px',
        cursor:      'pointer',
        fontSize:    '11px',
        fontFamily:  font.mono,
        fontWeight:  600,
        textAlign:   'left',
        transition:  `all ${motion.fast}`,
      }}
    >
      ⚙ {label}
    </button>
  );
}

function CreateCardButton({ onClick }) {
  const [hov, setHov] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        background:   color.yellow,
        border:       'none',
        borderRadius: radius.md,
        color:        '#000',
        fontSize:     '13px',
        fontWeight:   800,
        padding:      '7px 18px',
        cursor:       'pointer',
        fontFamily:   font.sans,
        display:      'flex',
        alignItems:   'center',
        gap:          '5px',
        boxShadow:    hov ? `0 0 22px ${color.yellow}60` : `0 0 12px ${color.yellow}30`,
        transform:    hov ? 'translateY(-1px)' : 'none',
        transition:   `all ${motion.fast}`,
      }}
    >
      <span style={{ fontSize: '16px', fontWeight: 900, lineHeight: 1, marginTop: '-1px' }}>+</span>
      Card
    </button>
  );
}
