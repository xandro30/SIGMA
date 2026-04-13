import { color, font, space, motion } from '../../../shared/tokens';
import { ChevronRight } from '../../../shared/components/Icons';

export default function MetricsBreadcrumb({ items }) {
  // items = [{ label: 'Metrics', onClick: fn }, { label: 'Trabajo', onClick: fn }, ...]
  return (
    <nav aria-label="Breadcrumb" style={{
      display: 'flex', alignItems: 'center', gap: space.xs,
      padding: `${space.sm} ${space['2xl']}`,
    }}>
      {items.map((item, i) => (
        <span key={i} style={{ display: 'flex', alignItems: 'center', gap: space.xs }}>
          {i > 0 && <ChevronRight size="12" style={{ color: color.muted2 }} />}
          {item.onClick ? (
            <button
              onClick={item.onClick}
              style={{
                background: 'none', border: 'none', cursor: 'pointer',
                fontFamily: font.sans, fontSize: '13px', fontWeight: 500,
                color: i < items.length - 1 ? color.muted : color.text,
                padding: 0, transition: `color ${motion.fast}`,
              }}
            >
              {item.label}
            </button>
          ) : (
            <span style={{
              fontFamily: font.sans, fontSize: '13px', fontWeight: 600,
              color: color.text,
            }}>
              {item.label}
            </span>
          )}
        </span>
      ))}
    </nav>
  );
}
