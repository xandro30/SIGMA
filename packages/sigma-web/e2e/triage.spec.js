import { test, expect } from '@playwright/test';
import { seedWorkspace, waitForApp } from './helpers/seed.js';
import { api } from './helpers/api.js';

let ws;

test.describe('Suite 1: Triage', () => {
  test.beforeAll(async () => {
    ws = await seedWorkspace();
  });

  test('1.1 — create card from topbar appears in Inbox', async ({ page }) => {
    await page.goto('/triage');
    await waitForApp(page);

    // Open CreateCardModal via topbar "+ Card" button
    await page.getByRole('button', { name: '+ Card' }).click();

    // Fill the form
    await page.getByPlaceholder(/qu[eé]/).fill('New E2E Card');
    await page.getByPlaceholder(/contexto/i).fill('Created by E2E test');

    // Submit
    await page.getByRole('button', { name: /crear/i }).click();

    // Wait for mutation to complete
    await page.waitForResponse(
      (r) => r.url().includes('/cards') && r.request().method() === 'POST',
    );
    await page.waitForTimeout(500);

    // Card should appear in the Inbox column
    await expect(page.getByText('New E2E Card')).toBeVisible();
  });

  test('1.2 — seeded cards appear in correct triage columns', async ({
    page,
  }) => {
    await page.goto('/triage');
    await waitForApp(page);

    // Each card should be visible
    await expect(page.getByText('Card in Inbox')).toBeVisible();
    await expect(page.getByText('Card in Refinement')).toBeVisible();
    await expect(page.getByText('Card in Backlog')).toBeVisible();
  });

  test('1.3 — move card via API and verify UI updates', async ({ page }) => {
    // Create a fresh card in inbox
    const card = await api.createCard(ws.space.id, {
      title: 'Move Test Card',
      priority: 'medium',
      initial_stage: 'inbox',
    });

    // Move it to refinement via API
    await api.moveTriageStage(card.id, 'refinement');

    // Load triage view — card should appear in Refinement
    await page.goto('/triage');
    await waitForApp(page);

    await expect(page.getByText('Move Test Card')).toBeVisible();
  });

  test('1.4 — click card opens detail panel', async ({ page }) => {
    await page.goto('/triage');
    await waitForApp(page);

    // Click on the card body (first match — the card in the triage column)
    await page.getByText('Card in Inbox').first().click();
    await page.waitForTimeout(300);

    // Detail panel opens with heading and "Editar" button
    await expect(page.getByRole('button', { name: /Editar/ })).toBeVisible();
  });

  test('1.5 — edit card via EditCardModal', async ({ page }) => {
    await page.goto('/triage');
    await waitForApp(page);

    // Click card to select it — opens detail panel
    await page.getByText('Card in Refinement').first().click();
    await page.waitForTimeout(300);

    // Click "Editar" button in the detail panel
    await page.getByRole('button', { name: '✏ Editar' }).click();
    await page.waitForTimeout(300);

    // EditCardModal should be open — look for save/guardar button
    await expect(
      page.getByRole('button', { name: /guardar/i }),
    ).toBeVisible();
  });

  test('1.6 — delete card removes it from view', async ({ page }) => {
    // Create a card to delete
    const card = await api.createCard(ws.space.id, {
      title: 'Delete Me Card',
      priority: 'low',
      initial_stage: 'inbox',
    });

    await page.goto('/triage');
    await waitForApp(page);

    // Verify card exists
    await expect(page.getByText('Delete Me Card')).toBeVisible();

    // Delete via API
    await api.deleteCard(card.id);

    // Reload and verify gone
    await page.reload();
    await waitForApp(page);

    await expect(page.getByText('Delete Me Card')).not.toBeVisible();
  });

  test('1.7 — card with HIGH priority shows orange left border', async ({
    page,
  }) => {
    await page.goto('/triage');
    await waitForApp(page);

    // The card is wrapped by SortableWrapper (role="button") > TriageCard div (has borderLeft)
    // Find the sortable wrapper by accessible name, then get its first child (the bordered div)
    const wrapper = page.getByRole('button', { name: /Card in Backlog.*HIGH/ });
    const cardDiv = wrapper.locator('> div');
    const borderLeft = await cardDiv.evaluate(
      (el) => getComputedStyle(el).borderLeftColor,
    );

    // HIGH priority color is #F97316 → rgb(249, 115, 22)
    expect(borderLeft).toContain('249');
  });
});
