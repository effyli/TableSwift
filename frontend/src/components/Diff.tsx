import React, { useState } from 'react';
import { File } from '../types/file';
import { actionService } from '../services/action.service';
import { Action } from '../types/action';

interface DiffProps {
  action: Action, 
  file: File,
  handleActionChange: (field: keyof Action, value: any) => void;
}

export const DiffViewer: React.FC<DiffProps> = ({ action, file, handleActionChange }) => {
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [isSearchActive, setIsSearchActive] = useState(false);
  const [prevSearchTerm, setPrevSearchTerm] = useState('');

  const handleSearch = async () => {
    if (!searchTerm.trim()) return clearSearch();
    if (searchTerm === prevSearchTerm) return;

    setIsSearching(true);
    try {
      const result = await actionService.searchAffectedRows(action.id, searchTerm);
      handleActionChange("file", {
        ...file!,
        data: result.data,
        loaded_rows: result.loaded_rows,
        total_rows: result.total_rows
      });
      setIsSearchActive(true);
    } catch (error) {
      alert('Search failed. Please try again.');
    } finally {
      setIsSearching(false);
      setPrevSearchTerm(searchTerm);
    }
  };

    const clearSearch = async () => {
      setSearchTerm('');
      setIsSearchActive(false);
      setPrevSearchTerm('');
      
      // Reset to initial data
      try {
        const result = await actionService.loadAffectedRows(action.id, 0);
        handleActionChange("file", {
          ...file!,
          data: result.data,
          loaded_rows: result.loaded_rows,
          total_rows: result.total_rows
        });
      } catch (error) {
        alert('Failed to reset data. Please try again.');
      }
    };

  const handleLoadMore = async () => {
    if (!file!.loaded_rows) return;

    setIsLoadingMore(true);
    try {
      let result;
      if (isSearchActive) {
        result = await actionService.searchAffectedRows(
          action.id,
          searchTerm,
          file!.loaded_rows
        );
      } else {
        result = await actionService.loadAffectedRows(
          action.id, 
          file.loaded_rows ?? 0
        );
      }

      handleActionChange("file", {
        ...file!,
        data: [...(file!.data || []), ...result.data!],
        loaded_rows: (file!.loaded_rows ?? 0) + result.loaded_rows!,
        total_rows: result.total_rows
      });
    } finally {
      setIsLoadingMore(false);
    }
  };

  if (!file?.data) {
    return (
      <div className="text-center p-4 bg-gray-100 rounded">
        No diff data available
      </div>
    );
  }

  const headers = file.data[0] ? Object.keys(file.data[0]) : [];

  return (
    <>
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
          disabled={isSearching || searchTerm === prevSearchTerm}
          className={`
            min-w-[100px] px-4 py-2 bg-indigo-600 text-white rounded-lg
            transition-colors flex items-center justify-center gap-2
            ${isSearching || searchTerm === prevSearchTerm
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
      {file.data.length > 0 ? (
        <>
          <table className="w-full">
            <thead className="sticky top-0 bg-black z-10">
              <tr className="text-sm text-gray-400 border-b border-black-lighter">
                {headers.map((header) => (
                  <th
                    key={header}
                    scope="col"
                    className="text-left font-semibold p-3"
                  >
                    {header}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="text-gray-300">
              {file.data.map((row, rowIndex) => (
                <tr key={rowIndex} className="border-b border-black-lighter">
                  {headers.map((header, colIndex) => (
                    <td
                      key={`${rowIndex}-${header}`}
                      className={`p-3 ${
                        colIndex === 0 ? 'text-green-500' : 'text-red-500'
                      }`}
                    >
                      {row[header]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {(file.loaded_rows ?? 0) < (file.total_rows ?? 0) && (
            <div className="mt-4 flex justify-center">
              <button 
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg 
                  transition-colors flex items-center gap-2
                  disabled:bg-indigo-600/50 disabled:cursor-not-allowed"
                onClick={handleLoadMore}
                disabled={isLoadingMore}
              >
                {isLoadingMore ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/20 border-t-white" />
                    Loading...
                  </>
                ) : (
                  'Load more rows'
                )}
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center p-4 bg-gray-100 rounded">
          No changes found in the diff file
        </div>
      )}
    </div>
    </>
  );
};
