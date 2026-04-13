import { ghost as g } from '../../../shared/tokens';

export default function GhostBlock({ top, height, label, hasOverlap }) {
  return (
    <div
      style={{
        position: 'absolute',
        top,
        left: '2px',
        right: '2px',
        height,
        background: hasOverlap ? g.backgroundCollision : g.background,
        border: hasOverlap ? g.borderCollision : g.border,
        borderRadius: '6px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        pointerEvents: 'none',
        zIndex: 10,
        transition: 'height 50ms linear',
      }}
    >
      {label && (
        <span style={{ ...g.label, userSelect: 'none' }}>
          {label}
        </span>
      )}
    </div>
  );
}
