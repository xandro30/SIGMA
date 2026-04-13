import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { color, font, space } from '../../shared/tokens';
import { useUIStore } from '../../shared/store/useUIStore';
import { useMetrics } from '../../entities/metrics/hooks/useMetrics';
import { planningApi } from '../../api/planning';
import MetricsHeader from './components/MetricsHeader';
import { KPIRow } from './components/KPICard';
import MetricsTree from './components/MetricsTree';

export default function MetricsView() {
  const spaceId = useUIStore(s => s.activeSpaceId);
  const [cycleId, setCycleId] = useState(null);
  const { data: metrics, isLoading, error } = useMetrics(spaceId, cycleId);
  const { data: allCycles } = useQuery({
    queryKey: ['allCycles', spaceId],
    queryFn: () => planningApi.listCycles(spaceId),
    enabled: !!spaceId,
  });
  const cycles = allCycles?.cycles ?? allCycles ?? [];

  if (!spaceId) {
    return (
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', color: color.muted2, fontSize: '13px' }}>
        Selecciona un Space para ver metricas
      </div>
    );
  }

  if (isLoading) {
    return (
      <div style={{ flex: 1, padding: space['2xl'] }}>
        <div className="animate-fade-in" style={{ display: 'flex', flexDirection: 'column', gap: space.lg }}>
          {/* Shimmer placeholders */}
          <div style={{ height: '80px', background: color.s2, borderRadius: '14px', animation: 'shimmer 1.5s infinite', backgroundSize: '200% 100%', backgroundImage: `linear-gradient(90deg, ${color.s2} 25%, ${color.s3} 50%, ${color.s2} 75%)` }} />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: space.lg }}>
            {[0, 1, 2, 3].map(i => (
              <div key={i} style={{ height: '120px', background: color.s2, borderRadius: '14px', animation: 'shimmer 1.5s infinite', animationDelay: `${i * 100}ms`, backgroundSize: '200% 100%', backgroundImage: `linear-gradient(90deg, ${color.s2} 25%, ${color.s3} 50%, ${color.s2} 75%)` }} />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    const isNoCycle = error.status === 404 || error.code === 'metrics_cycle_not_found';
    return (
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: space.lg }}>
        <div style={{
          width: '48px', height: '48px', borderRadius: '12px',
          background: isNoCycle ? color.yellowDim : 'rgba(239,68,68,0.12)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '22px',
        }}>
          {isNoCycle ? '📊' : '⚠'}
        </div>
        <span style={{ fontFamily: font.sans, fontSize: '15px', fontWeight: 600, color: color.text }}>
          {isNoCycle ? 'Sin ciclo activo' : 'Error cargando metricas'}
        </span>
        <span style={{ fontFamily: font.sans, fontSize: '13px', color: color.muted, textAlign: 'center', maxWidth: '360px' }}>
          {isNoCycle
            ? 'Crea un ciclo desde la seccion de planificacion (Schedule) y activalo para empezar a ver metricas.'
            : error.message}
        </span>
        {!isNoCycle && (
          <button
            onClick={() => setCycleId(null)}
            style={{
              padding: `${space.sm} ${space.lg}`,
              background: color.s3,
              border: 'none',
              borderRadius: '10px',
              color: color.text,
              fontFamily: font.sans,
              fontSize: '13px',
              fontWeight: 600,
              cursor: 'pointer',
            }}
          >
            Reintentar
          </button>
        )}
      </div>
    );
  }

  if (!metrics) return null;

  // Sum total budget across areas for the global KPI card
  const totalBudget = Object.values(metrics.areas ?? {}).reduce((sum, a) => sum + (a.budget_minutes ?? 0), 0);

  return (
    <div style={{ flex: 1, overflow: 'auto' }}>
      <MetricsHeader
        metrics={metrics}
        cycles={cycles}
        activeCycleId={cycleId ?? metrics.cycle_id}
        onCycleChange={setCycleId}
      />

      <div style={{ padding: `0 ${space['2xl']} ${space.xl}` }}>
        <KPIRow metrics={metrics.global_metrics} budgetTotal={totalBudget || null} />
      </div>

      <div style={{ padding: `0 ${space['2xl']} ${space['2xl']}` }}>
        <MetricsTree areas={metrics.areas} />
      </div>
    </div>
  );
}
