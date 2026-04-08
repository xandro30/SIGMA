import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { areasApi } from '../../../api/areas';

export function useAreas() {
  return useQuery({ queryKey: ['areas'], queryFn: areasApi.getAll });
}
export function useCreateArea() {
  const qc = useQueryClient();
  return useMutation({ mutationFn: areasApi.create, onSuccess: () => qc.invalidateQueries({ queryKey: ['areas'] }) });
}
export function useUpdateArea() {
  const qc = useQueryClient();
  return useMutation({ mutationFn: ({ id, ...data }) => areasApi.update(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['areas'] }) });
}
