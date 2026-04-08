import { api } from './client';
export const areasApi = {
  getAll:  ()          => api.get('/areas').then(r => r.areas),
  create:  (data)      => api.post('/areas', data),
  update:  (id, data)  => api.patch(`/areas/${id}`, data),
  remove:  (id)        => api.delete(`/areas/${id}`),
};
