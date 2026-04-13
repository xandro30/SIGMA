import { viewSelector as vs } from '../../../shared/tokens';

const CYCLE_TYPE_LABELS = {
  sprint: 'Sprint',
  quarter: 'Trimestre',
  semester: 'Semestre',
  annual: 'Año',
};

// Fixed order: Dia, Semana, Mes, then cycles by type order
const CYCLE_TYPE_ORDER = ['sprint', 'quarter', 'semester', 'annual'];

export default function ViewSelector({ activeView, onViewChange, activeCycles }) {
  const cycleViews = CYCLE_TYPE_ORDER
    .filter(type => (activeCycles ?? []).some(c => c.cycle_type === type))
    .map(type => ({
      id: `cycle:${type}`,
      label: CYCLE_TYPE_LABELS[type],
    }));

  const views = [
    { id: 'day', label: 'Dia' },
    { id: 'week', label: 'Semana' },
    { id: 'month', label: 'Mes' },
    ...cycleViews,
  ];

  return (
    <div style={vs.container}>
      {views.map(v => (
        <button
          key={v.id}
          onClick={() => onViewChange(v.id)}
          style={{
            ...vs.pill,
            ...(activeView === v.id ? vs.pillActive : vs.pillInactive),
          }}
        >
          {v.label}
        </button>
      ))}
    </div>
  );
}
