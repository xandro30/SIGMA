import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { epicsApi } from "../../../api/epics";
export function useEpicsBySpace(spaceId) {
  return useQuery({ queryKey:["epics","space",spaceId], queryFn:()=>epicsApi.getBySpace(spaceId), enabled:!!spaceId });
}
export function useEpic(id) {
  return useQuery({ queryKey:["epic",id], queryFn:()=>epicsApi.getById(id), enabled:!!id });
}
export function useCreateEpic(spaceId) {
  const qc = useQueryClient();
  return useMutation({ mutationFn:(data)=>epicsApi.create(spaceId,data), onSuccess:()=>qc.invalidateQueries({queryKey:["epics","space",spaceId]}) });
}
export function useUpdateEpic(id, spaceId) {
  const qc = useQueryClient();
  return useMutation({ mutationFn:(data)=>epicsApi.update(id,data), onSuccess:()=>{ qc.invalidateQueries({queryKey:["epic",id]}); qc.invalidateQueries({queryKey:["epics","space",spaceId]}); } });
}
