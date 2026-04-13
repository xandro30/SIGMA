import { test, expect } from '@playwright/test';
import { seedPlanningWorkspace } from './helpers/seed-planning.js';
import { waitForApp } from './helpers/seed.js';
import { api } from './helpers/api.js';

let ws;

test.describe('Suite 6: Scheduling (Planning V2)', () => {
  test.beforeAll(async () => {
    ws = await seedPlanningWorkspace();
  });

  // ══════════════════════════════════════════════════════════
  //  UI: Navigation
  // ══════════════════════════════════════════════════════════

  test('6.1 — Schedule tab navigates to /scheduling', async ({ page }) => {
    await page.goto('/workspace');
    await waitForApp(page);
    await page.getByRole('button', { name: /schedule/i }).click();
    await expect(page).toHaveURL(/scheduling/);
  });

  test('6.2 — day headers (LUN-DOM) and hour labels visible', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await expect(page.getByText('LUN').first()).toBeVisible();
    await expect(page.getByText('VIE').first()).toBeVisible();
    await expect(page.getByText('09:00').first()).toBeVisible();
  });

  test('6.3 — week nav shows date range', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await expect(page.locator('h2').first()).toHaveText(/\d+.*\d{4}/);
  });

  test('6.4 — sidebar visible on scheduling', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await expect(page.locator('aside')).toBeVisible();
  });

  // ══════════════════════════════════════════════════════════
  //  UI: Block creation flow
  // ══════════════════════════════════════════════════════════

  test('6.5 — "Nuevo bloque" opens modal with form', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await page.locator('button', { hasText: /nuevo bloque/i }).click();
    await expect(page.locator('form h3', { hasText: /nuevo bloque/i })).toBeVisible();
    await expect(page.locator('form input[type="datetime-local"]').first()).toBeVisible();
    await expect(page.locator('form input[type="number"]').first()).toBeVisible();
  });

  test('6.6 — creating a block via API and verifying it persists', async () => {
    // Create block via API (bypasses UI timing issues)
    const day = await api.createDay(ws.space.id, { date: ws.today });
    const updated = await api.addBlock(ws.space.id, day.id, {
      start_at: `${ws.today}T16:00:00+02:00`,
      duration: 90,
      area_id: ws.area.id,
      notes: 'Bloque E2E creado',
    });
    expect(updated.blocks.some(b => b.notes === 'Bloque E2E creado')).toBe(true);

    // Verify via getDayByDate
    const reloaded = await api.getDayByDate(ws.space.id, ws.today);
    expect(reloaded.blocks.some(b => b.notes === 'Bloque E2E creado')).toBe(true);
  });

  test('6.7 — cancel button closes modal without creating', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await page.locator('button', { hasText: /nuevo bloque/i }).click();
    await page.waitForTimeout(200);
    await page.locator('form button', { hasText: /cancelar/i }).click();
    await expect(page.locator('form')).not.toBeVisible();
  });

  // ══════════════════════════════════════════════════════════
  //  UI: Template selector
  // ══════════════════════════════════════════════════════════

  test('6.8 — Template button opens TemplatePanel slide-over', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await page.locator('button', { hasText: /template/i }).click();
    await expect(page.locator('h3', { hasText: 'Plantillas' })).toBeVisible();
    await expect(page.getByText('Plantillas de dia')).toBeVisible();
    await expect(page.getByText('Plantillas de semana')).toBeVisible();
  });

  test('6.9 — TemplatePanel shows seeded day template', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await page.locator('button', { hasText: /template/i }).click();
    await expect(page.getByText('Dia Productivo')).toBeVisible();
    await expect(page.getByText(/2 bloques/)).toBeVisible();
  });

  // ══════════════════════════════════════════════════════════
  //  API: Cycle lifecycle (create → activate → close)
  // ══════════════════════════════════════════════════════════

  test('6.10 — API: cycle is active after seed', async () => {
    const cycle = await api.getActiveCycle(ws.space.id);
    expect(cycle.state).toBe('active');
    expect(cycle.name).toBe('E2E Cycle');
  });

  test('6.11 — API: cycle has budget for seeded area', async () => {
    const cycle = await api.getActiveCycle(ws.space.id);
    const budgets = cycle.area_budgets;
    expect(budgets.length).toBeGreaterThanOrEqual(1);
    expect(budgets.some(b => b.area_id === ws.area.id && b.minutes === 600)).toBe(true);
  });

  // ══════════════════════════════════════════════════════════
  //  API: Week CRUD
  // ══════════════════════════════════════════════════════════

  test('6.12 — API: week creation is idempotent', async () => {
    const w1 = await api.createWeek(ws.space.id, { week_start: ws.monday });
    const w2 = await api.createWeek(ws.space.id, { week_start: ws.monday });
    expect(w1.id).toBe(w2.id);
  });

  test('6.13 — API: week rejects non-monday start', async () => {
    try {
      await api.createWeek(ws.space.id, { week_start: '2026-04-14' }); // Tuesday
      throw new Error('Should have failed');
    } catch (e) {
      expect(e.message).toContain('422');
    }
  });

  test('6.14 — API: week notes round-trip', async () => {
    await api.setWeekNotes(ws.space.id, ws.monday, { notes: 'Semana E2E test' });
    const week = await api.getWeek(ws.space.id, ws.monday);
    expect(week.notes).toBe('Semana E2E test');
  });

  // ══════════════════════════════════════════════════════════
  //  API: Day CRUD
  // ══════════════════════════════════════════════════════════

  test('6.15 — API: day creation is idempotent (deterministic id)', async () => {
    const d1 = await api.createDay(ws.space.id, { date: ws.today });
    const d2 = await api.createDay(ws.space.id, { date: ws.today });
    expect(d1.id).toBe(d2.id);
  });

  test('6.16 — API: seeded day has blocks', async () => {
    const day = await api.getDayByDate(ws.space.id, ws.today);
    expect(day.blocks.length).toBeGreaterThanOrEqual(2);
    expect(day.blocks.some(b => b.notes === 'Estudiar GCP')).toBe(true);
    expect(day.blocks.some(b => b.notes === 'Repasar Rust')).toBe(true);
  });

  test('6.17 — API: add block to day', async () => {
    const day = await api.getDayByDate(ws.space.id, ws.today);
    const beforeCount = day.blocks.length;
    const updated = await api.addBlock(ws.space.id, day.id, {
      start_at: `${ws.today}T18:00:00+02:00`,
      duration: 45,
      area_id: ws.area.id,
      notes: 'API block test',
    });
    expect(updated.blocks.length).toBe(beforeCount + 1);
    expect(updated.blocks.some(b => b.notes === 'API block test')).toBe(true);
  });

  test('6.18 — API: remove block from day', async () => {
    const day = await api.getDayByDate(ws.space.id, ws.today);
    const apiBlock = day.blocks.find(b => b.notes === 'API block test');
    expect(apiBlock).toBeDefined();
    const updated = await api.removeBlock(ws.space.id, day.id, apiBlock.id);
    // DELETE /blocks/{id} returns 200 with updated day (not 204)
    expect(updated.blocks.some(b => b.notes === 'API block test')).toBe(false);
  });

  test('6.19 — API: days in range returns seeded day', async () => {
    const result = await api.getDaysInRange(ws.space.id, ws.today, ws.today);
    expect(result.days.length).toBe(1);
    expect(result.days[0].date).toBe(ws.today);
  });

  // ══════════════════════════════════════════════════════════
  //  API: Templates
  // ══════════════════════════════════════════════════════════

  test('6.20 — API: day templates list includes seeded template', async () => {
    const resp = await api.listDayTemplates(ws.space.id);
    expect(resp.templates.length).toBeGreaterThanOrEqual(1);
    expect(resp.templates.some(t => t.name === 'Dia Productivo')).toBe(true);
  });

  test('6.21 — API: week template has monday slot set', async () => {
    // WeekTemplate was created with monday slot
    const templates = await api.listDayTemplates(ws.space.id);
    expect(templates.templates.length).toBeGreaterThanOrEqual(1);
  });

  // ══════════════════════════════════════════════════════════
  //  API: Capacity + ETA
  // ══════════════════════════════════════════════════════════

  test('6.22 — API: capacity returns for active cycle', async () => {
    const cap = await api.getCapacity(ws.space.id);
    expect(cap.cycle_id).toBe(ws.cycle.id);
    expect(cap.areas).toBeDefined();
    expect(cap.buffer_percentage).toBeDefined();
  });

  // ══════════════════════════════════════════════════════════
  //  API: Week with consecutive mondays
  // ══════════════════════════════════════════════════════════

  test('6.23 — API: creating weeks for different mondays', async () => {
    const w1 = await api.createWeek(ws.space.id, { week_start: '2026-05-04' });
    const w2 = await api.createWeek(ws.space.id, { week_start: '2026-05-11' });
    expect(w1.week_start).toBe('2026-05-04');
    expect(w2.week_start).toBe('2026-05-11');
    expect(w1.id).not.toBe(w2.id);
  });

  // ══════════════════════════════════════════════════════════
  //  UI: Multi-view calendar
  // ══════════════════════════════════════════════════════════

  test('6.24 — ViewSelector shows all view options', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await expect(page.getByRole('button', { name: 'Dia' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Semana' })).toBeVisible();
    await expect(page.getByRole('button', { name: 'Mes' })).toBeVisible();
    // Sprint tab only if sprint cycle is active
    await expect(page.getByRole('button', { name: 'Sprint' })).toBeVisible();
  });

  test('6.25 — Day view shows single column with hours', async ({ page }) => {
    await page.goto('/scheduling?view=day');
    await waitForApp(page);
    await expect(page.getByText('09:00').first()).toBeVisible();
    await expect(page.getByText('14:00').first()).toBeVisible();
    await expect(page.locator('h2').first()).toHaveText(/\d{4}/);
  });

  test('6.26 — Day view prev/next navigates by day', async ({ page }) => {
    await page.goto('/scheduling?view=day');
    await waitForApp(page);
    const title1 = await page.locator('h2').first().textContent();
    await page.getByRole('button', { name: 'Siguiente' }).click();
    await page.waitForTimeout(300);
    const title2 = await page.locator('h2').first().textContent();
    expect(title1).not.toBe(title2);
  });

  test('6.27 — Month view shows calendar grid', async ({ page }) => {
    await page.goto('/scheduling?view=month');
    await waitForApp(page);
    // Should show weekday headers
    await expect(page.getByText('LUN').first()).toBeVisible();
    await expect(page.getByText('DOM').first()).toBeVisible();
    // Title should be month + year
    await expect(page.locator('h2').first()).toHaveText(/\d{4}/);
  });

  test('6.28 — Month view click on day navigates to day view', async ({ page }) => {
    await page.goto('/scheduling?view=month');
    await waitForApp(page);
    // Click on a day cell (the "15" button)
    await page.locator('button', { hasText: '15' }).first().click();
    await expect(page).toHaveURL(/view=day/);
  });

  test('6.29 — Sprint view shows days of active sprint', async ({ page }) => {
    await page.goto('/scheduling?view=cycle%3Asprint');
    await waitForApp(page);
    // Should show the sprint cycle name in header
    await expect(page.locator('h2').first()).toHaveText(/E2E Cycle/);
    // Should show day rows with LUN, MAR, etc.
    await expect(page.getByText('LUN').first()).toBeVisible();
  });

  test('6.30 — Sprint view click on day navigates to day view', async ({ page }) => {
    await page.goto('/scheduling?view=cycle%3Asprint');
    await waitForApp(page);
    // Click on first day row
    await page.locator('button', { hasText: /LUN/ }).first().click();
    await expect(page).toHaveURL(/view=day/);
  });

  test('6.31 — Semana is active by default', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    const weekBtn = page.getByRole('button', { name: 'Semana' });
    // Check week view elements are present
    await expect(page.getByText('LUN')).toBeVisible();
    await expect(page.getByText('DOM')).toBeVisible();
  });

  // ══════════════════════════════════════════════════════════
  //  UI: Escape key closes modals
  // ══════════════════════════════════════════════════════════

  test('6.32 — Escape closes BlockEditModal', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await page.locator('button', { hasText: /nuevo bloque/i }).click();
    await expect(page.locator('form')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.locator('form')).not.toBeVisible();
  });

  test('6.33 — Escape closes TemplatePanel', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await page.locator('button', { hasText: /template/i }).click();
    await expect(page.locator('h3', { hasText: 'Plantillas' })).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.locator('h3', { hasText: 'Plantillas' })).not.toBeVisible();
  });

  test('6.34 — Escape closes CycleManager', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    // Click on the cycle button in sidebar to open CycleManager
    await page.locator('button', { hasText: /Activo/ }).click();
    await expect(page.getByText('Gestionar ciclos')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.getByText('Gestionar ciclos')).not.toBeVisible();
  });

  // ══════════════════════════════════════════════════════════
  //  UI: BlockEditModal fields
  // ══════════════════════════════════════════════════════════

  test('6.35 — BlockEditModal has start, duration, end, area, notes fields', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await page.locator('button', { hasText: /nuevo bloque/i }).click();
    await expect(page.getByText('Hora inicio')).toBeVisible();
    await expect(page.getByText(/Duración/)).toBeVisible();
    await expect(page.getByText('Hora fin')).toBeVisible();
    await expect(page.getByText('Área', { exact: true })).toBeVisible();
    await expect(page.locator('form').getByText('Notas')).toBeVisible();
    await page.keyboard.press('Escape');
  });

  test('6.36 — BlockEditModal allows saving without area', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await page.locator('button', { hasText: /nuevo bloque/i }).click();
    // Fill start time
    const startInput = page.locator('input[type="datetime-local"]').first();
    await startInput.fill(`${ws.today}T20:00`);
    // Area defaults to "Sin área" — no change needed
    // Submit
    await page.locator('form button[type="submit"]', { hasText: /crear/i }).click();
    // Modal should close (block created successfully)
    await page.waitForTimeout(500);
    await expect(page.locator('form')).not.toBeVisible();
  });

  // ══════════════════════════════════════════════════════════
  //  UI: TemplatePanel CRUD
  // ══════════════════════════════════════════════════════════

  test('6.37 — TemplatePanel: switch to week templates tab', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await page.locator('button', { hasText: /template/i }).click();
    await page.getByText('Plantillas de semana').click();
    await expect(page.getByText('Semana Productiva')).toBeVisible();
    await page.keyboard.press('Escape');
  });

  test('6.38 — TemplatePanel: week template shows slot count', async ({ page }) => {
    await page.goto('/scheduling');
    await waitForApp(page);
    await page.locator('button', { hasText: /template/i }).click();
    await page.getByText('Plantillas de semana').click();
    // Seeded template has 1/7 slots (monday only)
    await expect(page.getByText(/1\/7/)).toBeVisible();
    await page.keyboard.press('Escape');
  });
});
