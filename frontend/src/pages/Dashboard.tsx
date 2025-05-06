import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Split from 'react-split'
import { Sidebar } from '../components/Sidebar';
import { ActionHistory } from '../components/ActionHistory';
import { ContentView } from '../components/ContentView';
import { TopBar, ActiveView } from '../components/TopBar';
import { Project } from '../types/project';
import { File } from '../types/file';
import { projectService } from '../services/project.service';
import '../styles/components/Split.css';

export const Dashboard: React.FC = () => {
  const [activeView, setActiveView] = useState<ActiveView>('content');
  const [isSidebarOpen, setIsSidebarOpen] = useState(window.innerWidth > 1024);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024);
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(false);
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

  // Load project data when projectId changes
  useEffect(() => {
    const loadProject = async () => {
      if (!projectId) {
        setProject(null);
        return;
      }

      setIsLoading(true);
      try {
        const projectData = await projectService.getProjectDetails(projectId);
        setProject(projectData);
      } catch (error) {
        console.error('Failed to load project:', error);
        // TODO: Show error message to user
      } finally {
        setIsLoading(false);
      }
    };

    loadProject();
  }, [projectId]);

  const openProject = (projectId: string) => {
    navigate(`/dashboard/${projectId}`);
  };

  const handleFileDataUpdate = (newFile: File) => {
    if (project) {
      setProject({
        ...project,
        file: newFile
      });
    }
  };

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
          {isLoading ? (
            <div className="flex flex-1 items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-500 border-t-transparent"></div>
            </div>
          ) : projectId && project ? (
            <>
              {isMobile ? (
                // Mobile view - switch between views
                <>
                  {/* Action History - hidden on mobile when content view is active */}
                  <div className={`${activeView === 'actions' ? 'flex' : 'hidden'} flex-col flex-1`}>
                    <ActionHistory />
                  </div>

                  {/* Content View - hidden on mobile when actions view is active */}
                  <div className={`${activeView === 'content' ? 'flex' : 'hidden'} flex-1 min-w-0`}>
                    <ContentView 
                      file={project.file} 
                      projectId={projectId} 
                      onDataUpdate={handleFileDataUpdate}
                    />
                  </div>
                </>
              ) : (
                // Desktop view - split view with drag resize
                <Split 
                  className="flex flex-1 w-full"
                  sizes={[50, 50]}
                  minSize={300}
                  gutterSize={4}
                  snapOffset={0}
                >
                  <div className="flex flex-col overflow-auto">
                    <ActionHistory />
                  </div>
                  <div className="flex flex-col overflow-auto min-w-0">
                    <ContentView 
                      file={project.file} 
                      projectId={projectId} 
                      onDataUpdate={handleFileDataUpdate}
                    />
                  </div>
                </Split>
              )}
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

