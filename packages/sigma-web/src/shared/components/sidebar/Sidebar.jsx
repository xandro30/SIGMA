import { useLocation } from 'react-router-dom';
import { color, layout } from '../../tokens';
import WorkspaceSidebar from './WorkspaceSidebar';
import TriageSidebar from './TriageSidebar';
import ParaSidebar from './ParaSidebar';

export default function Sidebar() {
  const { pathname } = useLocation();
  const content = pathname.startsWith('/triage')
    ? <TriageSidebar />
    : pathname.startsWith('/workspace')
      ? <WorkspaceSidebar />
      : <ParaSidebar />;
  return (
    <aside style={{ width:layout.sidebarWidth, flexShrink:0, background:color.s1, borderRight:`1px solid ${color.border}`, overflowY:'auto', overflowX:'hidden', color:color.text, fontSize:'13px' }}>
      {content}
    </aside>
  );
}
