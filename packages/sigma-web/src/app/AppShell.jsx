import { color } from '../shared/tokens';
import Topbar from '../views/workspace/components/Topbar';
import Sidebar from '../shared/components/sidebar/Sidebar';
import CreateCardModal from '../shared/components/modals/CreateCardModal';
import { useUIStore } from '../shared/store/useUIStore';

export default function AppShell({ children }) {
  const createCardOpen = useUIStore(s => s.createCardOpen);

  return (
    <div style={{ height: '100vh', display: 'flex', flexDirection: 'column', background: `radial-gradient(ellipse 80% 50% at 50% -10%, rgba(245,197,24,0.04) 0%, ${color.bg} 60%)`, overflow: 'hidden' }}>
      <Topbar />
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <Sidebar />
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {children}
        </main>
      </div>
      {createCardOpen && <CreateCardModal />}
    </div>
  );
}
