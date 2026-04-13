import { useState, useMemo, useCallback } from 'react';
import { useQuery, useQueries } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { color, font, space } from '../../shared/tokens';
import { useUIStore } from '../../shared/store/useUIStore';
import { useMetrics } from '../../entities/metrics/hooks/useMetrics';
import { planningApi } from '../../api/planning';
import { useAreas } from '../../entities/area/hooks/useAreas';
import { useEpicsBySpace } from '../../entities/epic/hooks/useEpics';
import MetricsHeader from './components/MetricsHeader';
import { KPIRow } from './components/KPICard';
import MetricsDashboard from './components/MetricsDashboard';
import AreaDetailView from './components/AreaDetailView';
import ProjectDetailView from './components/ProjectDetailView';
import MetricsBreadcrumb from './components/MetricsBreadcrumb';

export default function MetricsView() {
  const spaceId = useUIStore(s => s.activeSpaceId);
  const [cycleId, setCycleId] = useState(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedAreaId = searchParams.get('area');
  const selectedProjectId = searchParams.get('project');

  const { data: metrics, isLoading, error } = useMetrics(spaceId, cycleId);
  const { data: areas } = useAreas(spaceId);
  const { data: epicsData } = useEpicsBySpace(spaceId);

  // Load projects from all areas in parallel
  const projectQueries = useQueries({
    queries: (areas ?? []).map(a => ({
      queryKey: ['projects', a.id],
      queryFn: async () => {
        const resp = await fetch(`${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/v1/areas/${a.id}/projects`);
        if (!resp.ok) return [];
        const data = await resp.json();
        return data.projects ?? data ?? [];
      },
      enabled: !!a.id,
    })),
  });
  const allProjects = useMemo(() =>
    projectQueries.flatMap(q => q.data ?? []),
    [projectQueries]
  );

  const { data: allCycles } = useQuery({
    queryKey: ['allCycles', spaceId],
    queryFn: () => planningApi.listCycles(spaceId),
    enabled: !!spaceId,
  });
  const cycles = allCycles?.cycles ?? allCycles ?? [];
  const allEpics = epicsData?.epics ?? epicsData ?? [];

  // Navigation handlers
  const navigateToOverview = useCallback(() => {
    setSearchParams({}, { replace: true });
  }, [setSearchParams]);

  const navigateToArea = useCallback((areaId) => {
    setSearchParams({ area: areaId }, { replace: true });
  }, [setSearchParams]);

  const navigateToProject = useCallback((projectId, areaId) => {
    setSearchParams({ project: projectId, area: areaId }, { replace: true });
  }, [setSearchParams]);

  // Resolve names for breadcrumb
  const selectedArea = (areas ?? []).find(a => a.id === selectedAreaId);
  const selectedProject = allProjects.find(p => p.id === selectedProjectId);

  // Find area data and project data from metrics
  const selectedAreaData = selectedAreaId ? metrics?.areas?.[selectedAreaId] : null;
  const selectedProjectData = useMemo(() => {
    if (!selectedProjectId || !selectedAreaData) return null;
    return selectedAreaData?.projects?.[selectedProjectId] ?? null;
  }, [selectedProjectId, selectedAreaData]);

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
          <div style={{ height: '80px', background: color.s2, borderRadius: '14px', animation: 'shimmer 1.5s infinite', backgroundSize: '200% 100%', backgroundImage: `linear-gradient(90deg, ${color.s2} 25%, ${color.s3} 50%, ${color.s2} 75%)` }} />
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: space.lg }}>
            {[0, 1, 2, 3].map(i => (
              <div key={i} style={{ height: '160px', background: color.s2, borderRadius: '14px', animation: 'shimmer 1.5s infinite', animationDelay: `${i * 100}ms`, backgroundSize: '200% 100%', backgroundImage: `linear-gradient(90deg, ${color.s2} 25%, ${color.s3} 50%, ${color.s2} 75%)` }} />
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
              background: color.s3, border: 'none', borderRadius: '10px',
              color: color.text, fontFamily: font.sans, fontSize: '13px', fontWeight: 600, cursor: 'pointer',
            }}
          >
            Reintentar
          </button>
        )}
      </div>
    );
  }

  if (!metrics) return null;

  const totalBudget = Object.values(metrics.areas ?? {}).reduce((sum, a) => sum + (a.budget_minutes ?? 0), 0);

  // Determine current view
  const isProjectDetail = !!selectedProjectId && !!selectedProjectData;
  const isAreaDetail = !!selectedAreaId && !!selectedAreaData && !isProjectDetail;
  const isDashboard = !isAreaDetail && !isProjectDetail;

  // Build breadcrumb
  const breadcrumbItems = [{ label: 'Metrics', onClick: navigateToOverview }];
  if (selectedArea && (isAreaDetail || isProjectDetail)) {
    breadcrumbItems.push({
      label: selectedArea.name,
      onClick: isProjectDetail ? () => navigateToArea(selectedAreaId) : undefined,
    });
  }
  if (selectedProject && isProjectDetail) {
    breadcrumbItems.push({ label: selectedProject.name });
  }

  return (
    <div style={{ flex: 1, overflow: 'auto' }}>
      <MetricsHeader
        metrics={metrics}
        cycles={cycles}
        activeCycleId={cycleId ?? metrics.cycle_id}
        onCycleChange={setCycleId}
      />

      {/* Breadcrumb — only show when drilled down */}
      {!isDashboard && <MetricsBreadcrumb items={breadcrumbItems} />}

      {/* Global KPIs — always visible */}
      {isDashboard && (
        <div style={{ padding: `0 ${space['2xl']} ${space.xl}` }}>
          <KPIRow metrics={metrics.global_metrics} budgetTotal={totalBudget || null} />
        </div>
      )}

      {/* Dashboard: Area Cards */}
      {isDashboard && (
        <MetricsDashboard
          areas={metrics.areas}
          areaLookup={areas}
          onAreaClick={navigateToArea}
        />
      )}

      {/* Area Detail */}
      {isAreaDetail && (
        <AreaDetailView
          areaId={selectedAreaId}
          areaData={selectedAreaData}
          areaName={selectedArea?.name ?? selectedAreaId}
          areaColorId={selectedArea?.color_id}
          globalMetrics={metrics.global_metrics}
          projectsLookup={allProjects}
          epicsLookup={allEpics}
          onProjectClick={(projId) => navigateToProject(projId, selectedAreaId)}
        />
      )}

      {/* Project Detail */}
      {isProjectDetail && (
        <ProjectDetailView
          projectId={selectedProjectId}
          projectData={selectedProjectData}
          projectName={selectedProject?.name ?? selectedProjectId}
          epicsLookup={allEpics}
          parentMetrics={selectedAreaData?.metrics}
          globalMetrics={metrics.global_metrics}
        />
      )}
    </div>
  );
}
