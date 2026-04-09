import { test, expect } from '@playwright/test';
import { seedWorkspace, waitForApp } from './helpers/seed.js';
import { api } from './helpers/api.js';

let ws;

test.describe('Suite 2: Workflow', () => {
  test.beforeAll(async () => {
    ws = await seedWorkspace();
  });

  test('2.1 — promote card from Backlog to first workflow state', async ({
    page,
  }) => {
    // Promote the backlog card via API
    const promoted = await api.promoteCard(
      ws.cards.backlog.id,
      ws.states.todo.id,
    );
    expect(promoted.workflow_state_id).toBe(ws.states.todo.id);
    expect(promoted.pre_workflow_stage).toBeNull();

    // Verify on Board
    await page.goto('/workspace');
    await waitForApp(page);

    await expect(page.getByText('Card in Backlog')).toBeVisible();
  });

  test('2.2 — move card between workflow states', async ({ page }) => {
    // Create a fresh card and promote it to To Do
    const card = await api.createCard(ws.space.id, {
      title: 'Move Test Card',
      priority: 'medium',
      initial_stage: 'backlog',
    });
    await api.promoteCard(card.id, ws.states.todo.id);

    // Move from To Do -> In Progress via API
    const moved = await api.moveCard(card.id, ws.states.wip.id);
    expect(moved.workflow_state_id).toBe(ws.states.wip.id);

    // Verify on Board
    await page.goto('/workspace');
    await waitForApp(page);

    await expect(page.getByText('Move Test Card')).toBeVisible();
  });

  test('2.3 — demote card from workflow back to triage', async ({ page }) => {
    // Create a fresh card, promote it, then demote it
    const card = await api.createCard(ws.space.id, {
      title: 'Demote Test Card',
      priority: 'low',
      initial_stage: 'backlog',
    });
    await api.promoteCard(card.id, ws.states.todo.id);

    // Demote back to backlog
    await api.demoteCard(card.id, 'backlog');

    // Verify card is NOT on the Board
    await page.goto('/workspace');
    await waitForApp(page);

    await expect(page.getByText('Demote Test Card')).not.toBeVisible();

    // Check it's back in triage
    await page.goto('/triage');
    await waitForApp(page);

    await expect(page.getByText('Demote Test Card')).toBeVisible();
  });

  test('2.4 — archive card removes it from Board', async ({ page }) => {
    // Create a card and promote it
    const card = await api.createCard(ws.space.id, {
      title: 'Archive Test Card',
      priority: 'medium',
      initial_stage: 'backlog',
    });
    await api.promoteCard(card.id, ws.states.todo.id);

    // Verify it appears on Board
    await page.goto('/workspace');
    await waitForApp(page);
    await expect(page.getByText('Archive Test Card')).toBeVisible();

    // Archive it
    await api.archiveCard(card.id);

    // Reload and verify gone
    await page.reload();
    await waitForApp(page);

    await expect(page.getByText('Archive Test Card')).not.toBeVisible();
  });

  test('2.5 — promote card via UI button (Workflow button in triage)', async ({
    page,
  }) => {
    // Create a fresh card in backlog
    const card = await api.createCard(ws.space.id, {
      title: 'Promote via UI',
      priority: 'high',
      initial_stage: 'backlog',
    });

    await page.goto('/triage');
    await waitForApp(page);

    // Click "→ Workflow" button scoped to the "Promote via UI" card
    // (avoids clicking the SortableWrapper which has the same text in accessible name)
    const cardEl = page.getByRole('button', { name: /Promote via UI/ });
    await cardEl.locator('button', { hasText: '→ Workflow' }).click();
    await page.waitForTimeout(300);

    // Promote modal shows workflow states — click "→ To Do" to promote
    const [response] = await Promise.all([
      page.waitForResponse(
        (r) => r.url().includes('/promote') && r.status() === 200,
      ),
      page.getByRole('button', { name: '→ To Do', exact: true }).click(),
    ]);

    await page.waitForTimeout(500);

    // Card should disappear from triage
    await expect(page.getByText('Promote via UI')).not.toBeVisible();

    // Verify it's on the board
    await page.goto('/workspace');
    await waitForApp(page);
    await expect(page.getByText('Promote via UI')).toBeVisible();
  });
});
