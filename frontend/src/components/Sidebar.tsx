import React, { useState, useEffect } from 'react';
import { Project } from '../services/project.service';
import "../styles/components/Sidebar.css";
import { FaRegTrashAlt } from "react-icons/fa";
import { projectService } from '../services/project.service';

interface SidebarProps {
  isSidebarOpen: boolean;
  setIsSidebarOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  isSidebarOpen,
  setIsSidebarOpen
}) => {
    const [uploadError, setUploadError] = useState<string|null>(null);
    const [projects, setProjects] = useState<Project[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [isUploading, setIsUploading] = useState(false);

    // Fetch projects on mount
    useEffect(() => {
        const fetchProjects = async () => {
            setIsLoading(true);
            try {
                const projectsList = await projectService.getProjects();
                setProjects(projectsList);
                console.log('Fetched projects:', projectsList); 
            } catch (error) {
                console.error('Failed to fetch projects:', error);
            } finally {
                setIsLoading(false);
            }
        };

        fetchProjects();
    }, []);

    const handleFileSelect = async (file: File) => {
        setUploadError(null);
        setIsUploading(true);

        // Validate file size (e.g., max 10MB)
        const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
        if (file.size > MAX_FILE_SIZE) {
            setUploadError('File size too large. Maximum size is 10MB.');
            setIsUploading(false);
            return;
        }

        try {
            console.log('Uploading file:', file);
            const result = await projectService.uploadFile(file);
            setProjects(prevProjects => [result, ...prevProjects]);
            
            // On mobile, close sidebar after successful upload
            if (window.innerWidth < 1024) {
                setIsSidebarOpen(false);
            }
        } catch (error) {
            console.error('Upload error:', error);
            setUploadError(error instanceof Error ? error.message : 'Failed to upload file');
        } finally {
            setIsUploading(false);
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
                            className={`w-full flex items-center justify-center px-4 py-6 border border-dotted rounded-lg hover:bg-black-lighter transition-colors cursor-pointer ${
                                uploadError ? 'border-red-500' : 'border-grey'
                            }`}
                        >
                            <span className="mr-2 text-lg">+</span>
                            <span className="text-gray-300">Select file</span>
                        </label>
                        <div className="mt-1 text-xs text-gray-500 px-1">
                            Only supports CSV files
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
                    
                    <div>
                        {/* Example projects - replace with actual data */}
                        {
                            [...Array(100)].map((_, index) => (
                                <div className='group flex gap-1 justify-between items-center text-gray-300 hover:bg-black-lighter px-3 py-3 rounded-lg cursor-pointer text-sm font-light' key={index}>
                                    <div
                                        key={index}
                                        className="text-ellipsis overflow-hidden whitespace-nowrap text-nowrap"
                                    >
                                        <span>
                                            project project project project {index + 1}
                                        </span>
                                    </div>
                                    <div className='opacity-0 group-hover:opacity-100 transition-opacity text-red'>
                                        <FaRegTrashAlt />
                                    </div>
                                </div>
                            ))
                        }
                    </div>
                </div>            
            </div>
        </div>
        <div onClick={() => setIsSidebarOpen(false)} className={`lg:hidden absolute top-0 h-full w-screen z-29 ${isSidebarOpen ? 'opacity-80 visible' : 'opacity-0 invisible'} transition-opacity duration-300 ease-in-out bg-black`}></div>
    </>
  );
};
