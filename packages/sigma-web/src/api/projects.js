import { api } from "./client";
export const projectsApi = {
  getByArea:  (areaId)      => api.get(`/areas/${areaId}/projects`).then((r) => r.projects),
  getById:    (id)          => api.get(`/projects/${id}`),
  create:     (areaId, data)=> api.post(`/areas/${areaId}/projects`, data),
  update:     (id, data)    => api.patch(`/projects/${id}`, data),
  remove:     (id)          => api.delete(`/projects/${id}`),
};
