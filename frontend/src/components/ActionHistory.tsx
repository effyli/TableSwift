import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ActionBase } from '../types/action';
import { actionService } from '../services/action.service';

interface ActionHistoryProps {
  actions: ActionBase[];
}

export const ActionHistory: React.FC<ActionHistoryProps> = ({ actions }) => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  const handleNewAction = async () => {
    if (!projectId) return;

    try {
      const newAction = await actionService.createAction({ project_id: projectId });
      navigate(`/dashboard/${projectId}/${newAction.id}`);
    } catch (error) {
      setError('Failed to create action');
      console.error('Error creating action:', error);
    }
  };

  return (
    <div className="bg-black-light border-r border-black-lighter min-h-0 h-full p-4 overflow-y-auto flex-1 flex flex-col">
      <button
      onClick={handleNewAction}
      className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors mb-6 flex items-center justify-center"
      >
      <span className="mr-2">+</span> New action
      </button>

      {error ? (
        <div className="text-red-500 text-center">{error}</div>
      ) : actions.length === 0 ? (
        <div className="text-gray-400 text-center">No actions yet. Create a new action to get started.</div>
      ) : (
        <div className="space-y-4">
          <table className="w-full">
          <thead>
            <tr className="text-sm text-gray-400">
            <th className="text-left font-semibold pb-2">Action</th>
            <th className="text-left font-semibold pb-2">Column</th>
            <th className="text-left font-semibold pb-2">Datetime</th>
            <th className="text-left font-semibold pb-2"></th>
            </tr>
          </thead>
          <tbody className="text-gray-300">
            {actions.map((action) => (
            <tr 
              key={action.id} 
              className="border-t border-black-lighter cursor-pointer hover:bg-black-lighter"
              onClick={() => navigate(`/dashboard/${projectId}/${action.id}`)}
            >                  <td className="py-3">{action.operation?.name || '(Not set)'}</td>
              <td className="py-3">{action.file_column || '(Not set)'}</td>
              <td className="py-3">{new Date(action.datetime).toLocaleString()}</td>
              <td className="py-3 text-right">
              <button
                onClick={(e) => {
                e.stopPropagation();
                // Add revert functionality here
                }}
                className="text-indigo-500 hover:text-indigo-400"
              >
                Revert
              </button>
              </td>
            </tr>
            ))}
          </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
