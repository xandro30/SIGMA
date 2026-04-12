import { api } from './client';

export const metricsApi = {
  getMetrics: (spaceId, cycleId) => {
    const params = cycleId ? `?cycle_id=${cycleId}` : '';
    return api.get(`/spaces/${spaceId}/metrics${params}`);
  },
  getSnapshot: (spaceId, cycleId) =>
    api.get(`/spaces/${spaceId}/metrics/snapshots/${cycleId}`),
};
