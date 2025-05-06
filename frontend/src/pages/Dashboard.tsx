import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Sidebar } from '../components/Sidebar';
import { ActionHistory } from '../components/ActionHistory';
import { ContentView } from '../components/ContentView';
import { TopBar, ActiveView } from '../components/TopBar';

export const Dashboard: React.FC = () => {
  const [activeView, setActiveView] = useState<ActiveView>('content');
  const [isSidebarOpen, setIsSidebarOpen] = useState(window.innerWidth > 1024);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024);
  const { projectId } = useParams();
  const navigate = useNavigate();

  // Listen for window resize
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    window.addEventListener('resize', handleResize);
    return () => {
      window.removeEventListener('resize', handleResize);
    };
  }, []);

  const openProject = (projectId: string) => {
    navigate(`/dashboard/${projectId}`);
  }

  

  return (
    <div className="flex flex-col h-screen bg-black-lighter overflow-hidden">
      <TopBar 
        onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)}
        activeView={activeView}
        setActiveView={setActiveView}
        isMobile={isMobile}
      />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <Sidebar 
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
          openProject={openProject}
          selectedProjectId={projectId}
        />

        {/* Main content area */}
        <div className="flex flex-1 flex-col lg:flex-row min-w-0">
          {projectId ? (
            <>
              {/* Action History - hidden on mobile when content view is active */}
              <div className={`
                ${isMobile ? (activeView === 'actions' ? 'flex' : 'hidden') : 'flex'}
                lg:flex flex-col flex-1
              `}>
                <ActionHistory />
              </div>

              {/* Content View - hidden on mobile when actions view is active */}
              <div className={`
                ${isMobile ? (activeView === 'content' ? 'flex' : 'hidden') : 'flex'}
                flex-1 min-w-0
              `}>
                <ContentView />
              </div>
            </>
          ) : (
            <div className="flex flex-1 items-center justify-center text-gray-500">
              <p>Select a project from the sidebar to get started</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

