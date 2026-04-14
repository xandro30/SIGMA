import { useMutation, useQueryClient } from '@tanstack/react-query';
import { trackingApi } from '../../../api/tracking';

export function useStartSession(spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data) => trackingApi.start(spaceId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['tracking', 'session', spaceId] }),
  });
}
