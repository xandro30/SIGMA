import { api } from './api.js';
import { clearFirestore } from './seed.js';

/**
 * Returns the Monday of the current week as ISO date string.
 */
function getCurrentMonday() {
  const d = new Date();
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  d.setDate(diff);
  return d.toISOString().split('T')[0];
}

function addDays(isoDate, n) {
  const d = new Date(isoDate + 'T00:00:00');
  d.setDate(d.getDate() + n);
  return d.toISOString().split('T')[0];
}

/**
 * Creates a complete planning test workspace:
 * - Clears Firestore first
 * - Space with workflow (To Do → In Progress → Done)
 * - Area (azul)
 * - Cycle (active, current month, with budget for the area)
 * - Week (current week)
 * - Day with 2 time blocks
 * - DayTemplate + WeekTemplate
 */
export async function seedPlanningWorkspace() {
  await clearFirestore();

  // Space + workflow
  // FINISH_STATE_ID is auto-created by the Space aggregate (hardcoded UUID)
  const FINISH_STATE_ID = '00000000-0000-4000-a000-000000000002';

  const space = await api.createSpace('Planning E2E');
  let updated = await api.addWorkflowState(space.id, 'To Do', 1);
  updated = await api.addWorkflowState(space.id, 'In Progress', 2);

  const states = updated.workflow_states;
  const todo = states.find((s) => s.name === 'To Do');
  const wip = states.find((s) => s.name === 'In Progress');
  const done = { id: FINISH_STATE_ID, name: 'Done (finish)' };

  await api.addTransition(space.id, todo.id, wip.id);
  await api.addTransition(space.id, wip.id, FINISH_STATE_ID);

  // Area
  const area = await api.createArea({
    name: 'Conocimiento',
    description: 'Area de estudio',
    color_id: 'azul',
  });

  // Cycle — covers current month
  const now = new Date();
  const monthStart = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
  const monthEnd = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split('T')[0];
  const cycle = await api.createCycle(space.id, {
    name: 'E2E Cycle',
    date_range: { start: monthStart, end: monthEnd },
  });
  await api.setBudget(space.id, cycle.id, { area_id: area.id, minutes: 600 });
  await api.activateCycle(space.id, cycle.id);

  // Week — current week
  const monday = getCurrentMonday();
  const week = await api.createWeek(space.id, { week_start: monday });

  // Day with blocks — today
  const today = new Date().toISOString().split('T')[0];
  const day = await api.createDay(space.id, { date: today });
  const todayDate = today; // e.g. "2026-04-12"
  const block1 = await api.addBlock(space.id, day.id, {
    start_at: `${todayDate}T09:00:00+02:00`,
    duration: 120,
    area_id: area.id,
    notes: 'Estudiar GCP',
  });
  const block2 = await api.addBlock(space.id, day.id, {
    start_at: `${todayDate}T14:00:00+02:00`,
    duration: 60,
    area_id: area.id,
    notes: 'Repasar Rust',
  });

  // DayTemplate
  const dayTemplate = await api.createDayTemplate(space.id, {
    name: 'Dia Productivo',
    blocks: [
      { start_at: { hour: 9, minute: 0 }, duration: 120, area_id: area.id, notes: 'Foco manana' },
      { start_at: { hour: 14, minute: 0 }, duration: 90, area_id: area.id, notes: 'Foco tarde' },
    ],
  });

  // WeekTemplate with Monday slot
  const weekTemplate = await api.createWeekTemplate(space.id, { name: 'Semana Productiva' });
  await api.setWeekSlot(space.id, weekTemplate.id, 'mon', { day_template_id: dayTemplate.id });

  return {
    space: updated,
    area,
    cycle,
    monday,
    today: todayDate,
    day,
    blocks: { block1: block1.blocks?.[0] ?? block1, block2: block2.blocks?.[1] ?? block2 },
    dayTemplate,
    weekTemplate,
    states: { todo, wip, done },
  };
}
