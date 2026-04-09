import { api } from './api.js';

const EMULATOR_URL = process.env.FIRESTORE_EMULATOR_URL || 'http://localhost:8080';
const PROJECT_ID = process.env.FIRESTORE_PROJECT_ID || 'sigma-local';

/**
 * Clears all data from the Firestore emulator.
 * Each suite calls this in beforeAll to start with a clean slate.
 */
export async function clearFirestore() {
  await fetch(
    `${EMULATOR_URL}/emulator/v1/projects/${PROJECT_ID}/databases/(default)/documents`,
    { method: 'DELETE' },
  );
}

/**
 * Creates a complete test workspace:
 * - Clears Firestore first (each suite starts fresh)
 * - Space with 3 workflow states (To Do -> In Progress -> Done)
 * - Area (azul) + Project + Epic
 * - 3 cards: one in each triage stage (inbox, refinement, backlog)
 */
export async function seedWorkspace() {
  await clearFirestore();

  // Space + workflow
  const space = await api.createSpace('E2E Test');

  let updated = await api.addWorkflowState(space.id, 'To Do', 1);
  updated = await api.addWorkflowState(space.id, 'In Progress', 2);
  updated = await api.addWorkflowState(space.id, 'Done', 3);

  const states = updated.workflow_states;
  const todo = states.find((s) => s.name === 'To Do');
  const wip = states.find((s) => s.name === 'In Progress');
  const done = states.find((s) => s.name === 'Done');

  await api.addTransition(space.id, todo.id, wip.id);
  await api.addTransition(space.id, wip.id, done.id);
  await api.addTransition(space.id, wip.id, todo.id);

  // PARA hierarchy
  const area = await api.createArea({
    name: 'Test Area',
    description: 'Area for E2E tests',
    color_id: 'azul',
  });

  const project = await api.createProject(area.id, {
    name: 'Test Project',
    description: 'Project for E2E tests',
  });

  const epic = await api.createEpic(space.id, {
    name: 'Test Epic',
    project_id: project.id,
    description: 'Epic for E2E tests',
  });

  // Cards in each triage stage
  const inboxCard = await api.createCard(space.id, {
    title: 'Card in Inbox',
    priority: 'low',
    initial_stage: 'inbox',
  });

  const refinementCard = await api.createCard(space.id, {
    title: 'Card in Refinement',
    priority: 'medium',
    initial_stage: 'refinement',
  });

  const backlogCard = await api.createCard(space.id, {
    title: 'Card in Backlog',
    priority: 'high',
    initial_stage: 'backlog',
    area_id: area.id,
    epic_id: epic.id,
    project_id: project.id,
  });

  return {
    space: updated,
    states: { todo, wip, done },
    area,
    project,
    epic,
    cards: {
      inbox: inboxCard,
      refinement: refinementCard,
      backlog: backlogCard,
    },
  };
}

/**
 * Fails fast if backend is unreachable.
 */
export async function ensureBackendReady() {
  const base = process.env.API_URL || 'http://localhost:8000';
  try {
    await api.health();
  } catch {
    throw new Error(
      `Backend not reachable at ${base}.\n` +
        'Local:\n' +
        '  1. docker compose up -d  (Firestore emulator + sigma-rest)\n' +
        '  2. cd packages/sigma-web && npm run e2e\n',
    );
  }
}

/**
 * Wait for the app to fully load: all initial fetches complete, React rendered.
 * Uses networkidle (500ms without network activity) instead of waitForResponse
 * to avoid race conditions where the response arrives before the listener.
 */
export async function waitForApp(page) {
  await page.waitForLoadState('networkidle');
}
