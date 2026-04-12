import { useMutation, useQueryClient } from '@tanstack/react-query';
import { planningApi } from '../../../api/planning';

export function useAddBlock(spaceId, weekStart) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ dayId, start_at, duration, area_id, notes }) =>
      planningApi.addBlock(spaceId, dayId, { start_at, duration, area_id, notes }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekDays', spaceId, weekStart] }),
  });
}

export function useUpdateBlock(spaceId, weekStart) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ dayId, blockId, ...data }) =>
      planningApi.updateBlock(spaceId, dayId, blockId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekDays', spaceId, weekStart] }),
  });
}

export function useRemoveBlock(spaceId, weekStart) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ dayId, blockId }) =>
      planningApi.removeBlock(spaceId, dayId, blockId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['weekDays', spaceId, weekStart] }),
  });
}
