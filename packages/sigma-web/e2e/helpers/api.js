const API_BASE = process.env.API_URL || 'http://localhost:8000';

async function request(method, path, body) {
  const options = {
    method,
    headers: { 'Content-Type': 'application/json' },
  };
  if (body !== undefined) options.body = JSON.stringify(body);

  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${method} ${path} -> ${res.status}: ${text}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Health
  health: () => request('GET', '/health'),

  // Spaces
  listSpaces: () => request('GET', '/v1/spaces'),
  createSpace: (name) => request('POST', '/v1/spaces', { name }),
  getSpace: (id) => request('GET', `/v1/spaces/${id}`),
  deleteSpace: (id) => request('DELETE', `/v1/spaces/${id}`),
  addWorkflowState: (spaceId, name, order) =>
    request('POST', `/v1/spaces/${spaceId}/workflow-states`, { name, order }),
  removeWorkflowState: (spaceId, stateId) =>
    request('DELETE', `/v1/spaces/${spaceId}/workflow-states/${stateId}`),
  addTransition: (spaceId, fromId, toId) =>
    request('POST', `/v1/spaces/${spaceId}/transitions`, { from_id: fromId, to_id: toId }),

  // Cards
  listCards: (spaceId) => request('GET', `/v1/spaces/${spaceId}/cards`),
  createCard: (spaceId, data) => request('POST', `/v1/spaces/${spaceId}/cards`, data),
  getCard: (id) => request('GET', `/v1/cards/${id}`),
  updateCard: (id, data) => request('PATCH', `/v1/cards/${id}`, data),
  deleteCard: (id) => request('DELETE', `/v1/cards/${id}`),
  moveCard: (id, targetStateId) =>
    request('PATCH', `/v1/cards/${id}/move`, { target_state_id: targetStateId }),
  promoteCard: (id, targetStateId = null) =>
    request('PATCH', `/v1/cards/${id}/promote`, { target_state_id: targetStateId }),
  demoteCard: (id, stage = 'backlog') =>
    request('PATCH', `/v1/cards/${id}/demote`, { stage }),
  moveTriageStage: (id, stage) =>
    request('PATCH', `/v1/cards/${id}/triage-stage`, { stage }),
  archiveCard: (id) => request('POST', `/v1/cards/${id}/archive`),

  // Areas
  listAreas: () => request('GET', '/v1/areas'),
  createArea: (data) => request('POST', '/v1/areas', data),
  updateArea: (id, data) => request('PATCH', `/v1/areas/${id}`, data),
  deleteArea: (id) => request('DELETE', `/v1/areas/${id}`),

  // Projects
  listProjects: (areaId) => request('GET', `/v1/areas/${areaId}/projects`),
  createProject: (areaId, data) =>
    request('POST', `/v1/areas/${areaId}/projects`, data),
  deleteProject: (id) => request('DELETE', `/v1/projects/${id}`),

  // Epics
  listEpicsBySpace: (spaceId) => request('GET', `/v1/spaces/${spaceId}/epics`),
  listEpicsByArea: (areaId) => request('GET', `/v1/areas/${areaId}/epics`),
  createEpic: (spaceId, data) =>
    request('POST', `/v1/spaces/${spaceId}/epics`, data),
  deleteEpic: (id) => request('DELETE', `/v1/epics/${id}`),
};
