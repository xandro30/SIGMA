import { useLocation } from 'react-router-dom';
import { color, layout } from '../../tokens';
import { useUIStore } from '../../store/useUIStore';
import WorkspaceSidebar from './WorkspaceSidebar';
import TriageSidebar from './TriageSidebar';
import ParaSidebar from './ParaSidebar';
import SchedulingSidebar from './SchedulingSidebar';

export default function Sidebar() {
  const { pathname } = useLocation();

  // Metrics view is full-width, no sidebar
  if (pathname.startsWith('/metrics')) return null;

  const content = pathname.startsWith('/triage')
    ? <TriageSidebar />
    : pathname.startsWith('/workspace')
      ? <WorkspaceSidebar />
      : pathname.startsWith('/scheduling')
        ? <SchedulingSidebarConnected />
        : <ParaSidebar />;

  return (
    <aside style={{ width:layout.sidebarWidth, flexShrink:0, background:color.s1, borderRight:`1px solid ${color.border}`, overflowY:'auto', overflowX:'hidden', color:color.text, fontSize:'13px' }}>
      {content}
    </aside>
  );
}

/**
 * Connected wrapper — reads data from the SchedulingView via store.
 * The SchedulingView writes its data to useUIStore._schedulingData
 * on every render, so the sidebar always has fresh data.
 */
function SchedulingSidebarConnected() {
  const data = useUIStore(s => s._schedulingData);
  if (!data) return <SchedulingSidebar weekStart={null} week={null} days={[]} areas={[]} />;

  return (
    <SchedulingSidebar
      weekStart={data.weekStart}
      week={data.week}
      days={data.days}
      areas={data.areas}
      cycle={data.activeCycle}
      onNotesChange={data.onNotesChange}
      onManageCycle={data.onManageCycle}
    />
  );
}
