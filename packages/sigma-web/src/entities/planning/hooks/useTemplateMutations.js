import { useMutation, useQueryClient } from '@tanstack/react-query';
import { planningApi } from '../../../api/planning';

export function useCreateDayTemplate(spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => planningApi.createDayTemplate(spaceId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['dayTemplates', spaceId] }),
  });
}

export function useUpdateDayTemplate(spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ templateId, data }) => planningApi.updateDayTemplate(spaceId, templateId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['dayTemplates', spaceId] }),
  });
}

export function useDeleteDayTemplate(spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (templateId) => planningApi.deleteDayTemplate(spaceId, templateId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['dayTemplates', spaceId] }),
  });
}

export function useApplyDayTemplate(spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ templateId, targetDate, replaceExisting }) =>
      planningApi.applyDayTemplate(spaceId, templateId, { target_date: targetDate, replace_existing: replaceExisting }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekDays', spaceId] }),
  });
}

export function useCreateWeekTemplate(spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => planningApi.createWeekTemplate(spaceId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekTemplates', spaceId] }),
  });
}

export function useDeleteWeekTemplate(spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (templateId) => planningApi.deleteWeekTemplate(spaceId, templateId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekTemplates', spaceId] }),
  });
}

export function useSetWeekTemplateSlot(spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ templateId, weekday, dayTemplateId }) =>
      planningApi.setWeekTemplateSlot(spaceId, templateId, weekday, { day_template_id: dayTemplateId }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekTemplates', spaceId] }),
  });
}

export function useClearWeekTemplateSlot(spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ templateId, weekday }) =>
      planningApi.clearWeekTemplateSlot(spaceId, templateId, weekday),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekTemplates', spaceId] }),
  });
}
