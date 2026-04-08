import { api } from "./client";
export const epicsApi = {
  getBySpace:   (spaceId)       => api.get(`/spaces/${spaceId}/epics`).then((r) => r.epics),
  getById:      (id)            => api.get(`/epics/${id}`),
  create:       (spaceId, data) => api.post(`/spaces/${spaceId}/epics`, data),
  update:       (id, data)      => api.patch(`/epics/${id}`, data),
  remove:       (id)            => api.delete(`/epics/${id}`),
};
