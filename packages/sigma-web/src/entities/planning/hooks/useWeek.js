import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { planningApi } from '../../../api/planning';

/** Fetch week metadata (notes, applied template, etc.) */
export function useWeek(spaceId, weekStart) {
  return useQuery({
    queryKey: ['week', spaceId, weekStart],
    queryFn: () => planningApi.getWeek(spaceId, weekStart),
    enabled: !!spaceId && !!weekStart,
    retry: false, // 404 = week not created yet, don't retry
  });
}

/** Fetch all days with blocks for a week range */
export function useWeekDays(spaceId, weekStart) {
  const end = weekStart ? addDays(weekStart, 6) : null;
  return useQuery({
    queryKey: ['weekDays', spaceId, weekStart],
    queryFn: () => planningApi.getDaysInRange(spaceId, weekStart, end).then(r => r.days),
    enabled: !!spaceId && !!weekStart,
  });
}

export function useCreateWeek(spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (weekStart) => planningApi.createWeek(spaceId, { week_start: weekStart }),
    onSuccess: (_, weekStart) => qc.invalidateQueries({ queryKey: ['week', spaceId, weekStart] }),
  });
}

export function useSetWeekNotes(spaceId, weekStart) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (notes) => planningApi.setWeekNotes(spaceId, weekStart, { notes }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['week', spaceId, weekStart] }),
  });
}

export function useApplyWeekTemplate(spaceId, weekStart) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ templateId, replaceExisting }) =>
      planningApi.applyTemplate(spaceId, weekStart, {
        template_id: templateId,
        replace_existing: replaceExisting ?? false,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['week', spaceId, weekStart] });
      qc.invalidateQueries({ queryKey: ['weekDays', spaceId, weekStart] });
    },
  });
}

export function useDeleteWeek(spaceId, weekStart) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => planningApi.deleteWeek(spaceId, weekStart),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['week', spaceId] });
      qc.invalidateQueries({ queryKey: ['weekDays', spaceId] });
    },
  });
}

// ── Helpers ────────────────────────────────────────────────
function addDays(isoDate, n) {
  const d = new Date(isoDate + 'T00:00:00');
  d.setDate(d.getDate() + n);
  return d.toISOString().split('T')[0];
}
