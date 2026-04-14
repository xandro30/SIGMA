import { useQuery } from '@tanstack/react-query';
import { trackingApi } from '../../../api/tracking';

export function useActiveSession(spaceId) {
  return useQuery({
    queryKey: ['tracking', 'session', spaceId],
    queryFn: () => trackingApi.getActive(spaceId),
    enabled: !!spaceId,
    refetchOnWindowFocus: false,
    retry: false,
  });
}
