import React, { useState, useEffect, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { ProjectSidebar } from '../types/project';
import "../styles/components/Sidebar.css";
import { FaRegTrashAlt } from "react-icons/fa";
import { projectService } from '../services/project.service';
import { ModalContext } from '../context/ModalContext';

interface SidebarProps {
    isMobile: boolean;
    isSidebarOpen: boolean;
    setIsSidebarOpen: (open: boolean) => void;
    openProject: (projectId: string) => void;
    selectedProjectId?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
    isMobile,
    isSidebarOpen,
    setIsSidebarOpen,
    openProject,
    selectedProjectId
}) => {
    const { handleModal, hideModal } = useContext(ModalContext);

    const [uploadError, setUploadError] = useState<string|null>(null);
    const [projects, setProjects] = useState<ProjectSidebar[]>([]);
    const [isLoadingProjects, setIsLoadingProjects] = useState(false);
    const [isUploading, setIsUploading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        // Fetch projects on mount in the sidebar
        const fetchProjects = async () => {
            setIsLoadingProjects(true);
            try {
                const projectsList = await projectService.getProjects();
                setProjects(projectsList);
            } catch (error) {
                console.error('Failed to fetch projects:', error);
            } finally {
                setIsLoadingProjects(false);
            }
        };

        fetchProjects();
    }, []);

    const handleFileSelect = async (file: File) => {
        if (isUploading) return;
        setUploadError(null);
        setIsUploading(true);

        try {
            const result = await projectService.uploadFile(file);
            setProjects(prevProjects => [result, ...prevProjects]);
            
            // On mobile, close sidebar after successful upload
            if (isMobile) {
                setIsSidebarOpen(false);
            }
            navigate(`/dashboard/${result.id}`);
        } catch (error) {
            console.error('Upload error:', error);
            setUploadError(error instanceof Error ? error.message : 'Failed to upload file');
        } finally {
            setIsUploading(false);
        }
    };

    const handleDeleteProject = async (projectId: string) => {
        try {
            await projectService.deleteProject(projectId);
            setProjects(prevProjects => prevProjects.filter(p => p.id !== projectId));
            navigate('/dashboard');
            hideModal();
        } catch (error) {
            console.error('Failed to delete project:', error);
        }
    };

  return (
    <>
        <div className={`
        absolute lg:static inset-y-0 left-0 z-30 
        bg-black-light border-r border-black-lighter
        transition-all duration-300 ease-in-out overflow-hidden
        top-[60px] lg:top-0
        ${isSidebarOpen ? 'translate-x-0 w-[250px]' : '-translate-x-full lg:translate-x-0 w-0'}
        `}
        >
            <div className='w-[250px] h-full flex flex-col'>
                <div className={`px-3 py-4 mt-4`}>
                    <div className="relative mb-4">
                        <input
                            type="file"
                            id="file-upload"
                            className="hidden"
                            onChange={(e) => {
                                if (e.target.files && e.target.files.length > 0) {
                                    handleFileSelect(e.target.files[0]);
                                }
                            }}
                            accept=".csv"
                        />
                        <label
                            htmlFor="file-upload"
                            className={`w-full flex items-center justify-center px-4 py-6 border border-dotted rounded-lg hover:bg-black-lighter transition-colors ${
                                uploadError ? 'border-red-500' : 'border-grey'
                            } ${isUploading ? 'cursor-wait opacity-50' : 'cursor-pointer'}`}
                        >
                            {isUploading ? (
                                <>
                                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-500 border-t-white mr-2"></div>
                                    <span className="text-gray-300">Uploading...</span>
                                </>
                            ) : (
                                <>
                                    <span className="mr-2 text-lg">+</span>
                                    <span className="text-gray-300">Select file</span>
                                </>
                            )}
                        </label>
                        <div className="mt-1 text-xs text-gray-500 px-1">
                            Only supports CSV files of 10MB or less.
                        </div>
                        {uploadError && (
                            <div className="mt-2 px-3 py-2 bg-red-500/10 border border-red-500/20 rounded text-red-500 text-sm animate-slideIn">
                                {uploadError}
                            </div>
                        )}
                    </div>
                </div>

                <div className={`px-3 flex-grow overflow-y-auto`} id="sidebar-projects">
                    <h2 className="text-sm font-semibold sticky top-0 bg-black-light py-2 px-3">
                        Projects
                    </h2>
                    
                    {
                    isLoadingProjects ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-2 border-gray-500 border-t-white mx-3 mt-2"></div>
                    ) : (
                        <div>
                            {
                            projects.length === 0 ? (
                                <div className="text-gray-500 text-sm text-center py-4">
                                    No projects available
                                </div>
                            ) : null
                            }
                            {(projects.length > 0) && projects.map((project, index) => (
                                <div 
                                    className={`group flex gap-1 justify-between items-center text-gray-300 px-3 py-3 rounded-lg cursor-pointer text-sm font-light
                                        ${selectedProjectId === project.id ? 'bg-black-lighter text-white' : 'hover:bg-black-lighter'}`}
                                    key={index} 
                                    onClick={() => {
                                        openProject(project.id); 
                                        if (isMobile) {
                                            setIsSidebarOpen(false);
                                        }
                                    }}
                                >
                                    <div
                                        key={index}
                                        className="text-ellipsis overflow-hidden whitespace-nowrap text-nowrap"
                                    >
                                        <span>
                                            {project.name}
                                        </span>
                                    </div>
                                    <div className='opacity-0 group-hover:opacity-100 transition-opacity text-red' onClick={(e) => {
                                        e.stopPropagation();
                                        handleModal({
                                            isOpen: true,
                                            title: 'Delete Project',
                                            message: `Are you sure you want to delete the project "${project.name}"? This action cannot be undone.`,
                                            primaryButton: {
                                                label: 'Delete',
                                                isLoading: false,
                                                onClick: async () => handleDeleteProject(project.id)
                                            },
                                            secondaryButton: {
                                                label: 'Cancel',
                                                onClick: () => hideModal()
                                            }
                                        });
                                    }}>
                                        <FaRegTrashAlt />
                                    </div>
                                </div>
                            ))
                            }
                        </div>
                    )
                    }
                </div>            
            </div>
        </div>
        <div onClick={() => setIsSidebarOpen(false)} className={`lg:hidden absolute top-0 h-full w-screen z-29 ${isSidebarOpen ? 'opacity-80 visible' : 'opacity-0 invisible'} transition-opacity duration-300 ease-in-out bg-black`}></div>
    </>
  );
};
