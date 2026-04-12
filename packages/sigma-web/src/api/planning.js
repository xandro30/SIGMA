import { api } from './client';

export const planningApi = {
  // Cycles
  listCycles:         (spaceId) => api.get(`/spaces/${spaceId}/cycles`),
  getActiveCycle:     (spaceId) => api.get(`/spaces/${spaceId}/cycles/active`),
  listActiveCycles:   (spaceId) => api.get(`/spaces/${spaceId}/cycles/active/all`),
  getCycle:           (spaceId, cycleId) => api.get(`/spaces/${spaceId}/cycles/${cycleId}`),
  createCycle:        (spaceId, data) => api.post(`/spaces/${spaceId}/cycles`, data),
  activateCycle:      (spaceId, cycleId) => api.post(`/spaces/${spaceId}/cycles/${cycleId}/activate`),
  closeCycle:         (spaceId, cycleId) => api.post(`/spaces/${spaceId}/cycles/${cycleId}/close`),
  setBudget:          (spaceId, cycleId, data) => api.put(`/spaces/${spaceId}/cycles/${cycleId}/budgets`, data),
  setBuffer:          (spaceId, cycleId, data) => api.patch(`/spaces/${spaceId}/cycles/${cycleId}/buffer`, data),

  // Weeks
  getWeek:            (spaceId, weekStart) => api.get(`/spaces/${spaceId}/weeks/${weekStart}`),
  createWeek:         (spaceId, data) => api.post(`/spaces/${spaceId}/weeks`, data),
  setWeekNotes:       (spaceId, weekStart, data) => api.put(`/spaces/${spaceId}/weeks/${weekStart}/notes`, data),
  applyTemplate:      (spaceId, weekStart, data) => api.post(`/spaces/${spaceId}/weeks/${weekStart}/apply-template`, data),
  deleteWeek:         (spaceId, weekStart) => api.delete(`/spaces/${spaceId}/weeks/${weekStart}`),

  // Days
  getDay:             (spaceId, dayId) => api.get(`/spaces/${spaceId}/days/${dayId}`),
  getDayByDate:       (spaceId, date) => api.get(`/spaces/${spaceId}/days/by-date/${date}`),
  getDaysInRange:     (spaceId, start, end) => api.get(`/spaces/${spaceId}/days/by-range?start=${start}&end=${end}`),
  createDay:          (spaceId, data) => api.post(`/spaces/${spaceId}/days`, data),
  addBlock:           (spaceId, dayId, data) => api.post(`/spaces/${spaceId}/days/${dayId}/blocks`, data),
  updateBlock:        (spaceId, dayId, blockId, data) => api.patch(`/spaces/${spaceId}/days/${dayId}/blocks/${blockId}`, data),
  removeBlock:        (spaceId, dayId, blockId) => api.delete(`/spaces/${spaceId}/days/${dayId}/blocks/${blockId}`),
  clearBlocks:        (spaceId, dayId) => api.delete(`/spaces/${spaceId}/days/${dayId}/blocks`),

  // Templates
  listDayTemplates:   (spaceId) => api.get(`/spaces/${spaceId}/day-templates`).then(r => r.templates),
  listWeekTemplates:  (spaceId) => api.get(`/spaces/${spaceId}/week-templates`).then(r => r.templates),

  // Capacity + ETA
  getCapacity:        (spaceId) => api.get(`/spaces/${spaceId}/capacity`),
  getCardEta:         (cardId, refDate) => api.get(`/cards/${cardId}/eta?reference_date=${refDate}`),
};
