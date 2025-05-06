import React, { useState } from 'react';
import { File } from '../types/file';
import { projectService } from '../services/project.service';

interface ContentViewProps {
  file: File;
  projectId: string;
  onDataUpdate: (newData: File) => void;
}

export const ContentView: React.FC<ContentViewProps> = ({ file, projectId, onDataUpdate }) => {
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearchActive, setIsSearchActive] = useState(false);

  if (!file || !file.data || file.data.length === 0) {
    return (
      <div className="bg-black min-h-0 h-full p-4 flex-1 flex items-center justify-center">
        <span className="text-gray-500">No data available</span>
      </div>
    );
  }

  // Get headers from the first data object
  const headers = Object.keys(file.data[0]);

  const handleSearch = async () => {
    if (!searchTerm.trim()) return;
    
    setIsSearching(true);
    try {
      const result = await projectService.searchProjectData(projectId, searchTerm);
      onDataUpdate({
        ...file,
        data: result.data,
        loaded_rows: result.loaded_rows,
        total_rows: result.total_rows
      });
      setIsSearchActive(true);
    } catch (error) {
      console.error('Failed to search:', error);
      // TODO: Show error message to user
    } finally {
      setIsSearching(false);
    }
  };

  const handleLoadMore = async () => {
    if (!file.loaded_rows) return;
    
    setIsLoadingMore(true);
    try {
      let result;
      if (isSearchActive) {
        result = await projectService.searchProjectData(
          projectId,
          searchTerm,
          file.loaded_rows
        );
      } else {
        result = await projectService.loadMoreRows(
          projectId,
          file.loaded_rows
        );
      }
      
      onDataUpdate({
        ...file,
        data: [...(file.data || []), ...result.data],
        loaded_rows: (file.loaded_rows ?? 0) + result.loaded_rows,
        total_rows: result.total_rows
      });
    } catch (error) {
      console.error('Failed to load more rows:', error);
      // TODO: Show error message to user
    } finally {
      setIsLoadingMore(false);
    }
  };
  
  const clearSearch = async () => {
    setSearchTerm('');
    setIsSearchActive(false);
    
    // Reset to initial data
    try {
      const result = await projectService.loadMoreRows(projectId, 0);
      onDataUpdate({
        ...file,
        data: result.data,
        loaded_rows: result.loaded_rows,
        total_rows: result.total_rows
      });
    } catch (error) {
      console.error('Failed to reset data:', error);
    }
  };
  
  return (
    <div className="bg-black min-h-0 h-full p-4 flex-1 flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <div className="text-gray-500">
          {file.loaded_rows} of {file.total_rows} rows
        </div>
        <div className="relative flex-1 max-w-md ml-4 flex gap-2">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search in all columns..."
            className="w-full bg-black-lighter text-white px-4 py-2 rounded-lg border border-black-lighter focus:outline-none focus:border-indigo-500"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                handleSearch();
              }
            }}
          />
          <button
            onClick={handleSearch}
            disabled={isSearching || !searchTerm.trim()}
            className={`
              min-w-[100px] px-4 py-2 bg-indigo-600 text-white rounded-lg
              transition-colors flex items-center justify-center gap-2
              ${isSearching || !searchTerm.trim() 
                ? 'opacity-50 cursor-not-allowed' 
                : 'hover:bg-indigo-700'}
            `}
          >
            {isSearching ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/20 border-t-white"></div>
                Searching...
              </>
            ) : (
              'Search'
            )}
          </button>
          {isSearchActive && (
            <button
              onClick={clearSearch}
              disabled={isSearching}
              className={`
                min-w-[100px] px-4 py-2 bg-gray-700 text-white rounded-lg 
                transition-colors flex items-center justify-center gap-2
                ${isSearching ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-600'}
              `}
            >
              {isSearching ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/20 border-t-white"></div>
                  Clearing...
                </>
              ) : (
                'Clear'
              )}
            </button>
          )}
        </div>
      </div>

      <div className="overflow-auto custom-scrollbar flex-1">
        <table className="w-full">
          <thead className="sticky top-0 bg-black z-10">
            <tr className="text-sm text-gray-400 border-b border-black-lighter">
              {headers.map((header) => (
                <th key={header} className="text-left font-semibold p-3">
                  {header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="text-gray-300">
            {file.data.map((row, index) => (
              <tr key={index} className="border-b border-black-lighter">
                {headers.map((header) => (
                  <td key={header} className="p-3">
                    {row[header]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {(file.loaded_rows ?? 0) < (file.total_rows ?? 0) && (
        <div className="mt-4 flex justify-center">
          <button 
            className={`
              bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg 
              transition-colors flex items-center gap-2
              disabled:bg-indigo-600/50 disabled:cursor-not-allowed
            `}
            onClick={handleLoadMore}
            disabled={isLoadingMore}
          >
            {isLoadingMore ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/20 border-t-white"></div>
                Loading...
              </>
            ) : (
              'Load more rows'
            )}
          </button>
        </div>
      )}
    </div>
  );
};
