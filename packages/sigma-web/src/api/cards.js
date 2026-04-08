import { api } from './client';
export const cardsApi = {
  getBySpace:       (spaceId)    => api.get(`/spaces/${spaceId}/cards`).then(r => r.cards),
  create:           (spaceId, d) => api.post(`/spaces/${spaceId}/cards`, d),
  update:           (id, data)   => api.patch(`/cards/${id}`, data),
  moveTriageStage:  (id, data)   => api.patch(`/cards/${id}/triage-stage`, data),
  move:             (id, data)   => api.patch(`/cards/${id}/move`, data),
  promote:          (id, data)   => api.patch(`/cards/${id}/promote`, data),
  demote:           (id, data)   => api.patch(`/cards/${id}/demote`, data),
  archive:          (id)         => api.delete(`/cards/${id}`),
};
