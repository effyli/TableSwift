import { useState, useEffect, use } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Split from 'react-split'
import { Sidebar } from '../components/Sidebar';
import { ActionHistory } from '../components/ActionHistory';
import { SingleAction } from '../components/SingleAction';
import { ContentView } from '../components/ContentView';
import { TopBar, ActiveView } from '../components/TopBar';
import { Project } from '../types/project';
import { File } from '../types/file';
import { Action, ActionBase } from '../types/action';
import { Operation } from '../types/operation';
import { projectService } from '../services/project.service';
import { operationService } from '../services/operation.service';
import '../styles/components/Split.css';

export const Dashboard: React.FC = () => {
  const [activeView, setActiveView] = useState<ActiveView>('content');
  const [isSidebarOpen, setIsSidebarOpen] = useState(window.innerWidth > 1024);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024);
  const [isLoadingProject, setIsLoadingProject] = useState(true);

  const [project, setProject] = useState<Project | null>(null);
  const [operations, setOperations] = useState<Operation[]>([]);
  const [fileColumns, setFileColumns] = useState<string[]>([]);
  
  const { projectId, actionId } = useParams();
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

  useEffect(() => {
    // Load project data when projectId changes
    if (!projectId) {
      setProject(null);
      return;
    }

    setIsLoadingProject(true);
    projectService.getProjectDetails(projectId, actionId).then((projectData) => {
      setProject(projectData);
      setFileColumns(projectData?.file?.data?.[0] ? Object.keys(projectData.file.data[0]) : []);
    }).catch((error) => {
      console.error('Failed to load project:', error);
      navigate('/dashboard'); // Redirect to dashboard if project not found
    }).finally(() => {
      setIsLoadingProject(false);
    
      // Load operations only when needed and project is loaded
      if (!operations || operations.length === 0) {
        setIsLoadingProject(true);
        operationService.getOperations().then((ops) => {
            setOperations(ops);
        }).catch((error) => {
            console.error('Error loading operations:', error);
        }).finally(() => {
            setIsLoadingProject(false);
        });
      }
    });

  }, [projectId]);

  const openProject = (projectId: string) => {
    navigate(`/dashboard/${projectId}`);
  };

  const handleSetActionUpdate = (action: Action | null) => {
    // Update the active action in the project when a single action is updated
    if (project && action) {
      // Update the ActionBase list item as well
      const updatedActions = project.actions.map(a => 
        a.id === action.id ? {
          id: action.id,
          project_id: action.project_id,
          datetime: action.datetime,
          operation: action.operation,
          file_column: action.file_column
        } : a
      ).sort((a, b) => new Date(b.datetime).getTime() - new Date(a.datetime).getTime());

      setProject({
        ...project,
        active_action: action,
        actions: updatedActions
      });
    }
  };

  const handleActionListUpdate = (actions: ActionBase[] | null, projectFile: File | undefined) => {
    // Update the action list in the project when an action is added or deleted
    if (project) {
      if (projectFile) {
        // Update project file and delete file from active action if projectFile is provided and thus an action is reverted
        const active_action = project.active_action ? {
          ...project.active_action,
          file: undefined
        } : null;

        setProject({
          ...project,
          actions: actions || [],
          file: projectFile,
          active_action
        });
      } else {
        setProject({
          ...project,
          actions: actions || [],
        });
      }
    }
  };

  const handleFilesDataUpdate = (newFile: File, actionNewFile: File | undefined) => {
    // Update the file data in the project and optionally in the active action
    if (project) {
      const updatedProject = {
        ...project,
        file: newFile
      };

      if (actionNewFile && project.active_action) {
        updatedProject.active_action = {
          ...project.active_action,
          file: actionNewFile
        };
        // Update the file in the actions list for the active action
        updatedProject.actions = updatedProject.actions.map(a => 
          a.id === project.active_action?.id ? { ...a, file: actionNewFile } : a
        );
      }

      setProject(updatedProject);
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
          isMobile={isMobile}
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
          openProject={openProject}
          selectedProjectId={projectId}
        />

        {/* Main content area */}
        <div className="flex flex-1 flex-col lg:flex-row min-w-0 h-full">
          {projectId ? (
            <>
              {isMobile ? (
                // Mobile view - switch between views
                <>
                  {/* Action History or Single Action - hidden on mobile when content view is active */}
                  <div className={`${activeView === 'actions' ? 'flex' : 'hidden'} flex-col flex-1 h-full`}>
                    {actionId ? (
                      <SingleAction
                        actions={project?.actions}
                        projectAction={project?.active_action}
                        isLoadingProject={isLoadingProject}
                        onActionUpdate={handleSetActionUpdate}
                        handleFileDataUpdate={handleFilesDataUpdate}
                        onActionListUpdate={handleActionListUpdate}
                        operations={operations}
                        fileColumns={fileColumns}
                      />
                    ) : (
                      <ActionHistory
                        actions={project?.actions}
                        onActionListUpdate={handleActionListUpdate}
                        isLoadingProject={isLoadingProject}
                      />
                    )}
                  </div>

                  {/* Content View - hidden on mobile when actions view is active */}
                  <div className={`${activeView === 'content' ? 'flex' : 'hidden'} flex-1 min-w-0`}>
                    <ContentView 
                      file={project?.file} 
                      projectId={projectId} 
                      onDataUpdate={handleFilesDataUpdate}
                      isLoadingProject={isLoadingProject}
                    />
                  </div>
                </>
              ) : (
                // Desktop view - split view with drag resize
                <Split 
                  className="flex flex-1 w-full"
                  sizes={[50, 50]}
                  minSize={350}
                  gutterSize={8}
                >
                  <div className="flex flex-col overflow-auto">
                    {actionId ? (
                      <SingleAction
                        actions={project?.actions}
                        projectAction={project?.active_action}
                        isLoadingProject={isLoadingProject}
                        onActionUpdate={handleSetActionUpdate}
                        handleFileDataUpdate={handleFilesDataUpdate}
                        onActionListUpdate={handleActionListUpdate}
                        operations={operations}
                        fileColumns={fileColumns}
                      />
                    ) : (
                      <ActionHistory
                        actions={project?.actions}
                        onActionListUpdate={handleActionListUpdate}
                        isLoadingProject={isLoadingProject}
                      />
                    )}
                  </div>
                  <div className="flex flex-col overflow-auto min-w-0">
                    <ContentView 
                      file={project?.file} 
                      projectId={projectId} 
                      onDataUpdate={handleFilesDataUpdate}
                      isLoadingProject={isLoadingProject}
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

