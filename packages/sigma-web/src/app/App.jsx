import { Routes, Route, Navigate } from 'react-router-dom';
import AppShell from './AppShell';
import WorkspaceLayout from '../views/workspace/components/WorkspaceLayout';
import TriageView from '../views/triage/TriageView';
import SpaceSettings from '../views/spaces/SpaceSettings';
import AreaList from '../views/areas/AreaList';
import AreaDetail from '../views/areas/AreaDetail';
import ProjectDetail from '../views/projects/ProjectDetail';
import EpicDetail from '../views/epics/EpicDetail';
import SchedulingView from '../views/scheduling/SchedulingView';
import MetricsView from '../views/metrics/MetricsView';
import { color, font } from '../shared/tokens';

function ComingSoon({ name }) {
  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:'12px', background:color.bg }}>
      <div style={{ background:color.yellow, width:'44px', height:'44px', borderRadius:'11px', display:'flex', alignItems:'center', justifyContent:'center', fontSize:'22px', fontWeight:900, color:'#000' }}>Σ</div>
      <p style={{ margin:0, fontSize:'13px', color:'#888', fontFamily:font.mono, fontWeight:700, letterSpacing:'0.1em' }}>{name.toUpperCase()} — PRÓXIMAMENTE</p>
    </div>
  );
}

export default function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/"                                                        element={<Navigate to="/workspace" replace />} />
        <Route path="/workspace"                                               element={<WorkspaceLayout />} />
        {/* backward compat */}
        <Route path="/workspace/pre-workflow"                                  element={<Navigate to="/triage" replace />} />
        <Route path="/triage"                                                  element={<TriageView />} />
        <Route path="/spaces/:spaceId/settings"                                element={<SpaceSettings />} />
        <Route path="/areas"                                                   element={<AreaList />} />
        <Route path="/areas/:areaId"                                           element={<AreaDetail />} />
        <Route path="/areas/:areaId/projects/:projectId"                       element={<ProjectDetail />} />
        <Route path="/areas/:areaId/projects/:projectId/epics/:epicId"         element={<EpicDetail />} />
        <Route path="/scheduling"                                              element={<SchedulingView />} />
        <Route path="/metrics"                                                 element={<MetricsView />} />
        <Route path="*"                                                        element={<Navigate to="/workspace" replace />} />
      </Routes>
    </AppShell>
  );
}
