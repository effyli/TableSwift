import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ActionBase } from '../types/action';
import { File } from '../types/file';
import { actionService } from '../services/action.service';
import { useModal } from '../context/ModalContext';

import { FaRegTrashAlt } from "react-icons/fa";
import { GrRevert } from "react-icons/gr";

interface ActionHistoryProps {
  actions: ActionBase[] | null | undefined;
  onActionListUpdate: (actions: ActionBase[] | null, projectFile?: File) => void;
  isLoadingProject: boolean;
}

export const ActionHistory: React.FC<ActionHistoryProps> = ({ actions, onActionListUpdate, isLoadingProject }) => {
  const [error, setError] = useState<string | null>(null);

  const { handleModal, hideModal } = useModal();
  const { projectId } = useParams();
  const navigate = useNavigate();

  const handleNewAction = async () => {
    if (!projectId) return;

    try {
      const newAction = await actionService.createAction({ project_id: projectId });
      // Update the action list with the new action
      const updatedActions = [newAction, ...(actions || [])];
      onActionListUpdate(updatedActions);
      navigate(`/dashboard/${projectId}/${newAction.id}`);
    } catch (error) {
      setError('Failed to create action');
    }
  };

  const deleteAction = async (actionId: number) => {
    if (!projectId) return;

    try {
      await actionService.deleteAction(actionId);
      // Delete the action from the list
      const updatedActions = actions?.filter((action: ActionBase) => action.id !== actionId) || null;
      onActionListUpdate(updatedActions);
    } catch (error) {
      setError('Failed to delete action');
    } finally {
      hideModal();
    }
  };

  const handleRevertAction = async (actionId: number) => {
    if (!projectId) return;
    try {
      const updatedProjectFile = await actionService.revertAction(actionId);

      // Set action file to null
      const updatedActions = actions?.map((action: ActionBase) =>
        action.id === actionId ? {
          ...action,
          file: undefined,
        } : action
      ) || null;

      onActionListUpdate(updatedActions, updatedProjectFile || undefined);
    } catch (error) {
      setError('Failed to revert action');
      alert('Failed to revert action. Please try again.');
    } finally {
      hideModal();
    }
  };

  return (
    <div className="bg-black-light border-r border-black-lighter min-h-0 h-full p-4 overflow-y-auto flex-1 flex flex-col">
      {isLoadingProject ? (
        // TODO custom loader
        <div className="flex flex-1 items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-500 border-t-transparent"></div>
        </div>
      ) : (
        <>
          <button
          onClick={handleNewAction}
          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors mb-6 flex items-center justify-center"
          >
          <span className="mr-2">+</span> New action
          </button>

          {error ? (
            <div className="text-red-500 text-center">{error}</div>
          ) : actions?.length === 0 ? (
            <div className="text-gray-400 text-center">No actions yet. Create a new action to get started.</div>
          ) : (
            <div className="space-y-4 overflow-x-auto custom-scrollbar">
              <table className="w-full whitespace-nowrap">
                <thead>
                  <tr className="text-sm text-gray-400">
                  <th className="text-left font-semibold p-4">Action</th>
                  <th className="text-left font-semibold p-4">Column</th>
                  <th className="text-left font-semibold p-4">Datetime</th>
                  <th className="text-left font-semibold p-4"></th>
                  </tr>
                </thead>
                <tbody className="text-gray-300">
                  {actions?.map((action) => (
                  <tr 
                    key={action.id} 
                    className="border-t border-black-lighter cursor-pointer hover:bg-black-lighter"
                    onClick={() => navigate(`/dashboard/${projectId}/${action.id}`)}
                  >
                    <td className="p-4">{action.operation?.name || '(Not set)'}</td>
                    <td className="p-4">{action.file_column || '(Not set)'}</td>
                    <td className="p-4">{new Date(action.datetime).toLocaleString()}</td>
                    <td className="p-4 text-right">
                    {
                      action.file ? (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleModal({
                              isOpen: true,
                              title: 'Revert Action',
                              message: 'Are you sure you want to revert this action? This action cannot be undone.',
                              primaryButton: {
                                label: 'Revert',
                                onClick: () => handleRevertAction(action.id),
                              },
                              secondaryButton: {
                                label: 'Cancel',
                                onClick: hideModal,
                              },
                            })
                          }}
                          className="text-red hover:text-red flex items-center justify-end gap-2 justify-self-center"
                        >
                          <GrRevert />
                          Revert
                        </button>
                      ) : (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleModal({
                              isOpen: true,
                              title: 'Delete Action',
                              message: 'Are you sure you want to delete this action? This action cannot be undone.',
                              primaryButton: {
                                label: 'Delete',
                                onClick: () => deleteAction(action.id),
                              },
                              secondaryButton: {
                                label: 'Cancel',
                                onClick: hideModal,
                              },
                            })
                          }}
                          className="text-red hover:text-red flex items-center justify-end gap-2 justify-self-center"
                        >
                          <FaRegTrashAlt />
                          Delete
                        </button>
                      )
                    }
                    </td>
                  </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
};
