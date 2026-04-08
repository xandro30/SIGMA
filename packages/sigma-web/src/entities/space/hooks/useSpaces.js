import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { spacesApi } from "../../../api/spaces";
export function useSpaces() {
  return useQuery({ queryKey:["spaces"], queryFn:spacesApi.getAll, staleTime:1000*30 });
}
export function useCreateSpace() {
  const qc = useQueryClient();
  return useMutation({ mutationFn:spacesApi.create, onSuccess:()=>qc.invalidateQueries({queryKey:["spaces"]}) });
}
