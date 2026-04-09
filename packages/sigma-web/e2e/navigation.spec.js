import { test, expect } from '@playwright/test';
import { seedWorkspace, waitForApp } from './helpers/seed.js';

let ws;

test.describe('Suite 5: Navigation & Layout', () => {
  test.beforeAll(async () => {
    ws = await seedWorkspace();
  });

  test('5.1 — topbar shows Board, Triage, Areas tabs', async ({ page }) => {
    await page.goto('/workspace');
    await waitForApp(page);

    await expect(page.getByText('Board', { exact: true })).toBeVisible();
    await expect(page.getByText('Triage', { exact: true })).toBeVisible();
    await expect(page.getByText('Áreas', { exact: true })).toBeVisible();
  });

  test('5.2 — navigate Board -> Triage -> Areas', async ({ page }) => {
    await page.goto('/workspace');
    await waitForApp(page);

    // Board -> Triage
    await page.getByText('Triage', { exact: true }).click();
    await expect(page).toHaveURL(/\/triage/);
    await expect(page.getByText('INBOX', { exact: true })).toBeVisible();

    // Triage -> Areas
    await page.getByText('Áreas', { exact: true }).click();
    await expect(page).toHaveURL(/\/areas/);

    // Areas -> Board
    await page.getByText('Board', { exact: true }).click();
    await expect(page).toHaveURL(/\/workspace/);
  });

  test('5.3 — sidebar changes with route', async ({ page }) => {
    // Workspace -> WorkspaceSidebar (has "Workflow" section)
    await page.goto('/workspace');
    await waitForApp(page);
    // "Workflow" appears as exact match (not "Pre-workflow")
    await expect(page.getByText('Workflow', { exact: true }).first()).toBeVisible();

    // Triage -> TriageSidebar
    await page.goto('/triage');
    await waitForApp(page);
    // TriageSidebar has "Triage" section (scoped to sidebar to avoid nav button match)
    await expect(page.getByRole('complementary').getByText('Triage')).toBeVisible();

    // Areas -> ParaSidebar (shows area navigation)
    await page.goto('/areas');
    await waitForApp(page);
    await expect(page.getByText('Áreas', { exact: true }).first()).toBeVisible();
  });

  test('5.4 — space selector shows active space', async ({ page }) => {
    await page.goto('/workspace');
    await waitForApp(page);

    // Space name visible in topbar selector (button with ▼)
    const selector = page.locator('header button').filter({ hasText: '▼' });
    await expect(selector).toContainText(ws.space.name);
  });
});
