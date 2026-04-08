import { api } from "./client";
export const spacesApi = {
  getAll:  ()       => api.get("/spaces").then((r) => r.spaces),
  getById: (id)     => api.get(`/spaces/${id}`),
  create:  (data)   => api.post("/spaces", data),
  delete:  (id)     => api.delete(`/spaces/${id}`),
  addWorkflowState:    (sid, data) => api.post(`/spaces/${sid}/workflow-states`, data),
  removeWorkflowState: (sid, stid) => api.delete(`/spaces/${sid}/workflow-states/${stid}`),
  addTransition:       (sid, data) => api.post(`/spaces/${sid}/transitions`, data),
};
