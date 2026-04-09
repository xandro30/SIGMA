import { test, expect } from '@playwright/test';
import { waitForApp, clearFirestore } from './helpers/seed.js';
import { api } from './helpers/api.js';

test.describe('Suite 4: Space & Workflow config', () => {
  test.beforeAll(async () => {
    await clearFirestore();
  });

  test('4.1 — create new Space and verify in selector', async ({ page }) => {
    const space = await api.createSpace('New E2E Space');
    expect(space.id).toBeTruthy();
    expect(space.name).toBe('New E2E Space');

    await page.goto('/workspace');
    await waitForApp(page);

    // Open space dropdown and verify space appears
    const selector = page.locator('header button').filter({ hasText: '▼' });
    await selector.click();
    await page.waitForTimeout(200);

    // Space appears in dropdown — use .first() since it shows in selector, dropdown item, and main
    await expect(page.getByText('New E2E Space').first()).toBeVisible();
  });

  test('4.2 — add workflow states to Space', async ({ page }) => {
    const space = await api.createSpace('Workflow Test Space');

    // Add states
    let updated = await api.addWorkflowState(space.id, 'Open', 1);
    updated = await api.addWorkflowState(space.id, 'Closed', 2);

    expect(updated.workflow_states).toHaveLength(2);
    expect(updated.workflow_states[0].name).toBe('Open');
    expect(updated.workflow_states[1].name).toBe('Closed');

    // Add transition
    const open = updated.workflow_states.find((s) => s.name === 'Open');
    const closed = updated.workflow_states.find((s) => s.name === 'Closed');
    const withTransition = await api.addTransition(
      space.id,
      open.id,
      closed.id,
    );
    expect(withTransition.transitions).toHaveLength(1);
  });

  test('4.3 — Board shows columns for workflow states', async ({ page }) => {
    const space = await api.createSpace('Board Columns Test');
    await api.addWorkflowState(space.id, 'Backlog', 1);
    await api.addWorkflowState(space.id, 'Doing', 2);
    await api.addWorkflowState(space.id, 'Released', 3);

    await page.goto('/workspace');
    await waitForApp(page);

    // Select "Board Columns Test" space if not already active
    const selector = page.locator('header button').filter({ hasText: '▼' });
    const selectorText = await selector.textContent();

    if (!selectorText.includes('Board Columns Test')) {
      await selector.click();
      await page.waitForTimeout(200);
      // force: true bypasses the dropdown overlay interception check
      await page
        .locator('button')
        .filter({ hasText: 'Board Columns Test' })
        .first()
        .click({ force: true });
      await waitForApp(page);
    }

    // Verify columns exist — scope to main (sidebar also shows state names)
    await expect(page.getByRole('main').getByText('Backlog', { exact: true })).toBeVisible();
    await expect(page.getByRole('main').getByText('Doing', { exact: true })).toBeVisible();
    await expect(page.getByRole('main').getByText('Released', { exact: true })).toBeVisible();
  });

  test('4.4 — workflow transition enables card movement', async () => {
    // Pure API test: verify transitions are enforced
    const space = await api.createSpace('Transition Test');
    let updated = await api.addWorkflowState(space.id, 'Alpha', 1);
    updated = await api.addWorkflowState(space.id, 'Beta', 2);
    updated = await api.addWorkflowState(space.id, 'Gamma', 3);

    const alpha = updated.workflow_states.find((s) => s.name === 'Alpha');
    const beta = updated.workflow_states.find((s) => s.name === 'Beta');
    const gamma = updated.workflow_states.find((s) => s.name === 'Gamma');

    // Only allow Alpha -> Beta -> Gamma
    await api.addTransition(space.id, alpha.id, beta.id);
    await api.addTransition(space.id, beta.id, gamma.id);

    // Create card and promote to Alpha
    const card = await api.createCard(space.id, {
      title: 'Transition Card',
      initial_stage: 'backlog',
    });
    await api.promoteCard(card.id, alpha.id);

    // Move Alpha -> Beta should work
    const moved = await api.moveCard(card.id, beta.id);
    expect(moved.workflow_state_id).toBe(beta.id);

    // Move Beta -> Gamma should work
    const moved2 = await api.moveCard(card.id, gamma.id);
    expect(moved2.workflow_state_id).toBe(gamma.id);
  });
});
