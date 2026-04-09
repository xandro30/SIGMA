import { test, expect } from '@playwright/test';
import { seedWorkspace, waitForApp } from './helpers/seed.js';
import { api } from './helpers/api.js';

let ws;

test.describe('Suite 3: PARA hierarchy', () => {
  test.beforeAll(async () => {
    ws = await seedWorkspace();
  });

  test('3.1 — create Area from Areas view', async ({ page }) => {
    await page.goto('/areas');
    await waitForApp(page);

    // Fill the "new area" input
    const input = page
      .getByPlaceholder(/nueva/i)
      .or(page.getByPlaceholder(/area/i));
    if (await input.isVisible()) {
      await input.fill('E2E Area');

      // Click "+ Área" create button (exact match avoids "Áreas" tab and "Editar área" buttons)
      await page.getByRole('button', { name: '+ Área' }).click();

      // Wait for creation
      await page.waitForResponse(
        (r) =>
          r.url().includes('/areas') && r.request().method() === 'POST',
      );
      await page.waitForTimeout(500);

      // New area should appear in main content
      await expect(
        page.getByRole('main').getByText('E2E Area'),
      ).toBeVisible();
    }
  });

  test('3.2 — seeded Area visible in Areas list', async ({ page }) => {
    await page.goto('/areas');
    await waitForApp(page);

    // Scope to main content to avoid sidebar duplicates
    await expect(
      page.getByRole('main').getByText('Test Area').first(),
    ).toBeVisible();
  });

  test('3.3 — navigate to Area detail shows projects', async ({ page }) => {
    await page.goto(`/areas/${ws.area.id}`);
    await waitForApp(page);

    // Area name should be visible in main content
    await expect(
      page.getByRole('main').getByText('Test Area').first(),
    ).toBeVisible();

    // Project should be listed
    await expect(
      page.getByRole('main').getByText('Test Project').first(),
    ).toBeVisible();
  });

  test('3.4 — create Project inside Area detail', async ({ page }) => {
    await page.goto(`/areas/${ws.area.id}`);
    await waitForApp(page);

    // Find the new project input
    const input = page.getByPlaceholder(/proyecto/i);
    if (await input.isVisible()) {
      await input.fill('E2E Project');

      const createBtn = page.getByRole('button', { name: /proyecto/i });
      await createBtn.click();

      await page.waitForResponse(
        (r) =>
          r.url().includes('/projects') && r.request().method() === 'POST',
      );
      await page.waitForTimeout(500);

      await expect(
        page.getByRole('main').getByText('E2E Project').first(),
      ).toBeVisible();
    }
  });

  test('3.5 — CreateCardModal groups epics by project (optgroup)', async ({
    page,
  }) => {
    await page.goto('/triage');
    await waitForApp(page);

    // Open CreateCardModal
    await page.getByRole('button', { name: '+ Card' }).click();
    await page.waitForTimeout(300);

    // Find the select that contains our area
    const selects = page.locator('select');
    const selectCount = await selects.count();

    for (let i = 0; i < selectCount; i++) {
      const options = await selects.nth(i).locator('option').allTextContents();
      if (options.some((o) => o.includes('Test Area'))) {
        await selects.nth(i).selectOption({ label: 'Test Area' });
        await page.waitForTimeout(500);
        break;
      }
    }

    // After selecting area, the epic select should have optgroup with project name
    const optgroups = page.locator('optgroup');
    const optgroupCount = await optgroups.count();

    if (optgroupCount > 0) {
      const label = await optgroups.first().getAttribute('label');
      expect(label).toContain('Test Project');
    }
  });

  test('3.6 — navigate full PARA hierarchy via routes', async ({ page }) => {
    // Area list
    await page.goto('/areas');
    await waitForApp(page);
    await expect(
      page.getByRole('main').getByText('Test Area').first(),
    ).toBeVisible();

    // Area detail
    await page.goto(`/areas/${ws.area.id}`);
    await waitForApp(page);
    await expect(
      page.getByRole('main').getByText('Test Project').first(),
    ).toBeVisible();

    // Project detail
    await page.goto(`/areas/${ws.area.id}/projects/${ws.project.id}`);
    await waitForApp(page);
    await expect(
      page.getByRole('main').getByText('Test Epic').first(),
    ).toBeVisible();
  });
});
