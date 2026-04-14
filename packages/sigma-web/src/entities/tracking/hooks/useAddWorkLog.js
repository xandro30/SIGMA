import { useMutation, useQueryClient } from '@tanstack/react-query';
import { trackingApi } from '../../../api/tracking';

export function useAddWorkLog(cardId, spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => trackingApi.addWorkLog(cardId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['cards', spaceId] }),
  });
}
