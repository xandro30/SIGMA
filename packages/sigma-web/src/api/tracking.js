import { api } from './client';

export const trackingApi = {
  // GET /spaces/{spaceId}/tracking/sessions/active → WorkSession | null (204 = null)
  getActive: (spaceId) =>
    api.get(`/spaces/${spaceId}/tracking/sessions/active`),

  // POST /spaces/{spaceId}/tracking/sessions
  // body: { description, work_minutes, break_minutes, num_rounds }
  start: (spaceId, data) =>
    api.post(`/spaces/${spaceId}/tracking/sessions`, data),

  // POST /spaces/{spaceId}/tracking/sessions/rounds
  completeRound: (spaceId) =>
    api.post(`/spaces/${spaceId}/tracking/sessions/rounds`, {}),

  // POST /spaces/{spaceId}/tracking/sessions/resume
  resume: (spaceId) =>
    api.post(`/spaces/${spaceId}/tracking/sessions/resume`, {}),

  // DELETE /spaces/{spaceId}/tracking/sessions?save=true|false
  stop: (spaceId, save) =>
    api.delete(`/spaces/${spaceId}/tracking/sessions?save=${save}`),

  // POST /cards/{cardId}/work-log
  // body: { description, minutes }
  addWorkLog: (cardId, data) =>
    api.post(`/cards/${cardId}/work-log`, data),
};
