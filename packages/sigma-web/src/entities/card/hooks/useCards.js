import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { cardsApi } from '../../../api/cards';

export function useCards(spaceId) {
  return useQuery({ queryKey: ['cards', spaceId], queryFn: () => cardsApi.getBySpace(spaceId), enabled: !!spaceId });
}
export function useCreateCard(spaceId) {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (data) => cardsApi.create(spaceId, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['cards', spaceId] }) });
}
export function useUpdateCard(spaceId) {
  const qc = useQueryClient();
  return useMutation({ mutationFn: ({ id, ...data }) => cardsApi.update(id, data), onSuccess: () => qc.invalidateQueries({ queryKey: ['cards', spaceId] }) });
}
export function useMoveCard(spaceId) {
  const qc = useQueryClient();
  return useMutation({ mutationFn: ({ cardId, targetStateId }) => cardsApi.move(cardId, { target_state_id: targetStateId }), onSuccess: () => qc.invalidateQueries({ queryKey: ['cards', spaceId] }) });
}
export function usePromoteCard(spaceId) {
  const qc = useQueryClient();
  return useMutation({ mutationFn: ({ cardId, targetStateId }) => cardsApi.promote(cardId, { target_state_id: targetStateId ?? null }), onSuccess: () => qc.invalidateQueries({ queryKey: ['cards', spaceId] }) });
}
export function useDemoteCard(spaceId) {
  const qc = useQueryClient();
  return useMutation({ mutationFn: ({ cardId, stage }) => cardsApi.demote(cardId, { stage }), onSuccess: () => qc.invalidateQueries({ queryKey: ['cards', spaceId] }) });
}
export function useMoveTriageStage(spaceId) {
  const qc = useQueryClient();
  return useMutation({ mutationFn: ({ cardId, stage }) => cardsApi.moveTriageStage(cardId, { stage }), onSuccess: () => qc.invalidateQueries({ queryKey: ['cards', spaceId] }) });
}
export function useArchiveCard(spaceId) {
  const qc = useQueryClient();
  return useMutation({ mutationFn: (id) => cardsApi.archive(id), onSuccess: () => qc.invalidateQueries({ queryKey: ['cards', spaceId] }) });
}
