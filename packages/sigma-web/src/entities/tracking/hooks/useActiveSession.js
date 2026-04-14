import { useQuery } from '@tanstack/react-query';
import { trackingApi } from '../../../api/tracking';

// Normalizes backend shape → flat shape expected by components:
//   session.timer.work_minutes → session.work_minutes
//   session.completed_rounds   → session.current_round (1-indexed)
function normalizeSession(data) {
  if (!data) return null;
  return {
    ...data,
    work_minutes:  data.timer?.work_minutes  ?? 25,
    break_minutes: data.timer?.break_minutes ?? 5,
    num_rounds:    data.timer?.num_rounds    ?? 4,
    current_round: (data.completed_rounds ?? 0) + 1,
  };
}

export function useActiveSession(spaceId) {
  return useQuery({
    queryKey: ['tracking', 'session', spaceId],
    queryFn: () => trackingApi.getActive(spaceId),
    enabled: !!spaceId,
    refetchOnWindowFocus: false,
    retry: false,
    select: normalizeSession,
  });
}
