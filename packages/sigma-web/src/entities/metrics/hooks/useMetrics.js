import { useQuery } from '@tanstack/react-query';
import { metricsApi } from '../../../api/metrics';

export function useMetrics(spaceId, cycleId) {
  return useQuery({
    queryKey: ['metrics', spaceId, cycleId ?? 'active'],
    queryFn: () => metricsApi.getMetrics(spaceId, cycleId),
    enabled: !!spaceId,
    staleTime: cycleId ? 1000 * 60 * 30 : 1000 * 60 * 2, // snapshots cache 30min, on-demand 2min
  });
}

export function useSnapshot(spaceId, cycleId) {
  return useQuery({
    queryKey: ['snapshot', spaceId, cycleId],
    queryFn: () => metricsApi.getSnapshot(spaceId, cycleId),
    enabled: !!spaceId && !!cycleId,
    staleTime: 1000 * 60 * 60, // snapshots are immutable, cache 1h
  });
}
