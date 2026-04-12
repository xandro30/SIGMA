import { useQuery } from '@tanstack/react-query';
import { planningApi } from '../../../api/planning';

export function useDayTemplates(spaceId) {
  return useQuery({
    queryKey: ['dayTemplates', spaceId],
    queryFn: () => planningApi.listDayTemplates(spaceId),
    enabled: !!spaceId,
  });
}

export function useWeekTemplates(spaceId) {
  return useQuery({
    queryKey: ['weekTemplates', spaceId],
    queryFn: () => planningApi.listWeekTemplates(spaceId),
    enabled: !!spaceId,
  });
}
