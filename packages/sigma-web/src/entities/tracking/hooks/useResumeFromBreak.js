import { useMutation, useQueryClient } from '@tanstack/react-query';
import { trackingApi } from '../../../api/tracking';

export function useResumeFromBreak(spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => trackingApi.resume(spaceId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tracking', 'session', spaceId] }),
  });
}
