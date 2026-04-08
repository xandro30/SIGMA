import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { projectsApi } from "../../../api/projects";
export function useProjects(areaId) {
  return useQuery({ queryKey:["projects",areaId], queryFn:()=>projectsApi.getByArea(areaId), enabled:!!areaId });
}
export function useProject(id) {
  return useQuery({ queryKey:["project",id], queryFn:()=>projectsApi.getById(id), enabled:!!id });
}
export function useCreateProject(areaId) {
  const qc = useQueryClient();
  return useMutation({ mutationFn:(data)=>projectsApi.create(areaId,data), onSuccess:()=>qc.invalidateQueries({queryKey:["projects",areaId]}) });
}
export function useUpdateProject(id, areaId) {
  const qc = useQueryClient();
  return useMutation({ mutationFn:(data)=>projectsApi.update(id,data), onSuccess:()=>{ qc.invalidateQueries({queryKey:["project",id]}); qc.invalidateQueries({queryKey:["projects",areaId]}); } });
}
