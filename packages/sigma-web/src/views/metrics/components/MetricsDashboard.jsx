import { color, font, space } from '../../../shared/tokens';
import AreaCard from './AreaCard';

export default function MetricsDashboard({ areas, areaLookup, onAreaClick }) {
  const areaEntries = Object.entries(areas ?? {});

  if (areaEntries.length === 0) {
    return (
      <div style={{
        padding: space['2xl'], textAlign: 'center',
        fontFamily: font.sans, fontSize: '13px', color: color.muted2,
      }}>
        Sin datos por área en este ciclo
      </div>
    );
  }

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
      gap: space.lg,
      padding: `0 ${space['2xl']} ${space['2xl']}`,
    }}>
      {areaEntries.map(([areaId, areaData]) => {
        const area = (areaLookup ?? []).find(a => a.id === areaId);
        return (
          <AreaCard
            key={areaId}
            areaId={areaId}
            areaName={area?.name ?? areaId.slice(0, 8)}
            areaColorId={area?.color_id}
            metrics={areaData.metrics}
            budget={areaData.budget_minutes}
            onClick={() => onAreaClick(areaId)}
          />
        );
      })}
    </div>
  );
}
