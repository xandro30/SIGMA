import { useState } from 'react';
import { color, font, space, radius, elevation, motion, getAreaHex } from '../../../shared/tokens';
import { BarChart, Clock, ChevronRight } from '../../../shared/components/Icons';
import { formatDays } from '../../../shared/dateUtils';
import BulletChart from './BulletChart';

export default function AreaCard({ areaId, areaName, areaColorId, metrics, budget, onClick }) {
  const [hov, setHov] = useState(false);
  const hex = getAreaHex(areaColorId);
  const cards = metrics?.total_cards_completed ?? 0;
  const cycle = metrics?.avg_cycle_time_minutes;
  const lead = metrics?.avg_lead_time_minutes;
  const consumed = metrics?.consumed_minutes ?? 0;
  const totalHours = Math.floor(consumed / 60);

  return (
    <button
      onClick={onClick}
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      aria-label={`${areaName}: ${cards} cards completadas, ${formatDays(cycle)} cycle time`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: space.xl,
        padding: `${space['2xl']} ${space.xl}`,
        background: hov ? color.s3 : color.s2,
        border: hov ? `1px solid ${hex}60` : `1px solid ${color.border}`,
        borderLeft: `3px solid ${hex}`,
        borderRadius: radius.lg,
        cursor: 'pointer',
        textAlign: 'left',
        transition: `all ${motion.fast}`,
        boxShadow: hov ? elevation[2] : elevation[1],
        minWidth: 0,
      }}
    >
      {/* Header: area name + total hours */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: space.sm }}>
          <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: hex, flexShrink: 0 }} />
          <span style={{ fontFamily: font.sans, fontSize: '17px', fontWeight: 700, color: color.text }}>
            {areaName}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: space.xs }}>
          <span style={{ fontFamily: font.mono, fontSize: '15px', fontWeight: 600, color: hex }}>
            {totalHours}h
          </span>
          <ChevronRight size="14" style={{ color: color.muted }} />
        </div>
      </div>

      {/* Stats row: cards, cycle, lead */}
      <div style={{ display: 'flex', gap: space.lg }}>
        <StatItem icon={BarChart} value={cards} label="cards" color={color.text} />
        <StatItem icon={Clock} value={cycle != null ? formatDays(cycle) : '—'} label="cycle" color={color.muted} />
        <StatItem icon={Clock} value={lead != null ? formatDays(lead) : '—'} label="lead" color={color.muted} />
      </div>

      {/* Budget bar */}
      {budget > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <BulletChart consumed={consumed} budget={budget} fillColor={hex} />
        </div>
      )}
    </button>
  );
}

function StatItem({ icon: Icon, value, label, color: textColor }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: space.sm, minWidth: 0 }}>
      <Icon size="16" style={{ color: textColor, flexShrink: 0, opacity: 0.6 }} />
      <div style={{ minWidth: 0 }}>
        <div style={{ fontFamily: font.mono, fontSize: '18px', fontWeight: 700, color: textColor, lineHeight: 1 }}>
          {value}
        </div>
        <div style={{ fontFamily: font.mono, fontSize: '10px', color: color.muted2, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          {label}
        </div>
      </div>
    </div>
  );
}
