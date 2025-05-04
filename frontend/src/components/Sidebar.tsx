import React from 'react';
import "../styles/components/Sidebar.css";
import { FaRegTrashAlt } from "react-icons/fa";

interface SidebarProps {
  onFileSelect: (file: File) => void;
  uploadError?: string|null;
  isSidebarOpen: boolean;
  setIsSidebarOpen: (open: boolean) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ 
  onFileSelect, 
  uploadError, 
  isSidebarOpen,
  setIsSidebarOpen
}) => {
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
                                    onFileSelect(e.target.files[0]);
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
