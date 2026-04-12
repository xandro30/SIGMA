/** Date utilities for the scheduling view. All dates as ISO strings (YYYY-MM-DD). */

const DAY_NAMES_SHORT = ['DOM', 'LUN', 'MAR', 'MIE', 'JUE', 'VIE', 'SAB'];
const MONTH_NAMES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];

/** Get the Monday of the week containing `date`. */
export function getMonday(date = new Date()) {
  const d = new Date(date);
  const day = d.getDay(); // 0=Sun
  const diff = d.getDate() - day + (day === 0 ? -6 : 1);
  d.setDate(diff);
  return toISO(d);
}

/** Add N days to an ISO date string. */
export function addDays(isoDate, n) {
  const d = parseISO(isoDate);
  d.setDate(d.getDate() + n);
  return toISO(d);
}

/** Get the 7 dates (Mon-Sun) of the week starting at `monday`. */
export function getWeekDates(monday) {
  return Array.from({ length: 7 }, (_, i) => addDays(monday, i));
}

/** ISO week number (ISO 8601). */
export function getWeekNumber(isoDate) {
  const d = parseISO(isoDate);
  const tmp = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  tmp.setUTCDate(tmp.getUTCDate() + 4 - (tmp.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(tmp.getUTCFullYear(), 0, 1));
  return Math.ceil(((tmp - yearStart) / 86400000 + 1) / 7);
}

/** "S16 · 13–19 Abr 2026" */
export function formatWeekRange(monday) {
  const start = parseISO(monday);
  const end = parseISO(addDays(monday, 6));
  const sDay = start.getDate();
  const eDay = end.getDate();
  const month = MONTH_NAMES[end.getMonth()];
  const year = end.getFullYear();
  const weekNum = getWeekNumber(monday);
  const range = start.getMonth() === end.getMonth()
    ? `${sDay}–${eDay} ${month} ${year}`
    : `${sDay} ${MONTH_NAMES[start.getMonth()]}–${eDay} ${month} ${year}`;
  return `S${weekNum} · ${range}`;
}

/** Short day name: "LUN", "MAR", etc. */
export function dayNameShort(isoDate) {
  return DAY_NAMES_SHORT[parseISO(isoDate).getDay()];
}

/** Day of month: 14, 15, etc. */
export function dayOfMonth(isoDate) {
  return parseISO(isoDate).getDate();
}

/** Is this date today? */
export function isToday(isoDate) {
  return isoDate === toISO(new Date());
}

/** Is this a weekend (Sat/Sun)? */
export function isWeekend(isoDate) {
  const day = parseISO(isoDate).getDay();
  return day === 0 || day === 6;
}

/** Parse "HH:MM" or ISO datetime to { hour, minute }. */
export function parseTime(timeStr) {
  if (!timeStr) return { hour: 0, minute: 0 };
  if (timeStr.includes('T')) {
    const d = new Date(timeStr);
    return { hour: d.getHours(), minute: d.getMinutes() };
  }
  const [h, m] = timeStr.split(':').map(Number);
  return { hour: h, minute: m };
}

/** Format minutes to "Xh Ym" or "Xh". */
export function formatDuration(minutes) {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  if (h === 0) return `${m}m`;
  if (m === 0) return `${h}h`;
  return `${h}h ${m}m`;
}

/** Format minutes to "X.Xd" (days = minutes / 1440). */
export function formatDays(minutes) {
  if (minutes == null) return '—';
  const days = minutes / 1440;
  return `${days.toFixed(1)}d`;
}

// ── Internal helpers ─────────────────────────────────
function parseISO(s) {
  return new Date(s + 'T00:00:00');
}

function toISO(d) {
  // Use local date components, not UTC (toISOString converts to UTC which shifts the date)
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}
