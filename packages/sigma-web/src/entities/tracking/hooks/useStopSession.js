import { useMutation, useQueryClient } from '@tanstack/react-query';
import { trackingApi } from '../../../api/tracking';

export function useStopSession(spaceId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (save) => trackingApi.stop(spaceId, save),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['tracking', 'session', spaceId] });
      qc.invalidateQueries({ queryKey: ['cards'] });
    },
  });
}
