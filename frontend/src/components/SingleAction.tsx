import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Action, ActionUpdate } from '../types/action';
import { Operation } from '../types/operation';
import { actionService } from '../services/action.service';

interface SingleActionProps {
    action: Action | null | undefined;
    onActionUpdate: (action: Action | null) => void;
    operations: Operation[];
    fileColumns: string[];
}

export const SingleAction: React.FC<SingleActionProps> = ({ action, onActionUpdate, operations, fileColumns }) => {
  const { projectId, actionId } = useParams();
  const navigate = useNavigate();
  const [selectedOperation, setSelectedOperation] = useState<number | null>(action?.operation?.id || null);
  const [fileColumn, setFileColumn] = useState(action?.file_column || '');
  const [description, setDescription] = useState(action?.description || '');
  const [isLoading, setIsLoading] = useState(true);
  const [isLoadingSaving, setIsLoadingSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load the action only when needed
    if ((!action && actionId) || (action && action.id !== parseInt(actionId ?? ''))) {
      onActionUpdate(null);
      setIsLoading(true);
      
      actionService.getAction(parseInt(actionId!)).then((actionData) => {
        onActionUpdate(actionData);
      }).catch((error) => {
        setError('Failed to load action');
        console.error('Error loading action:', error);
      }).finally(() => {
        setIsLoading(false);
      });
    } else {
      setIsLoading(false);
    }
  }, []);
  
  // Update all form fields when action changes
  useEffect(() => {
    if (action) {
      setSelectedOperation(action.operation?.id || null);
      setFileColumn(action.file_column || '');
      setDescription(action.description || '');
    } else {
      // Reset form if action is null
      setSelectedOperation(null);
      setFileColumn('');
      setDescription('');
    }
  }, [action]);

  const handleSave = async () => {
    if (!actionId || !selectedOperation || !fileColumn || !description) {
      setError('Please fill in all fields');
      return;
    }

    setIsLoadingSaving(true);
    try {
      const actionUpdate: ActionUpdate = {
        id: parseInt(actionId),
        operation_id: selectedOperation,
        file_column: fileColumn,
        description: description
      };

      const updatedAction = await actionService.updateAction(parseInt(actionId), actionUpdate);
      onActionUpdate(updatedAction);
      // TODO show the generated labels
    } catch (error) {
      setError('Failed to save action');
      console.error('Error saving action:', error);
    } finally {
      setIsLoadingSaving(false);
    }
  };

  const handleBack = () => {
    if (projectId) {
      navigate(`/dashboard/${projectId}`);
    }
  };

  return (
    <div className="bg-black-light border-r border-black-lighter p-4 h-full flex flex-col overflow-auto">
      <div className="sticky top-0 flex items-center mb-6 justify-between">
        <button
          onClick={handleBack}
          className="text-indigo-500 hover:text-indigo-400 mr-4"
        >
          ← Back to Actions
        </button>
        {!isLoading && (
          <button
            onClick={handleSave}
            disabled={isLoadingSaving || !selectedOperation}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            {isLoadingSaving ? 'Saving...' : 'Save Action'}
          </button>  
        )}
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-500 text-red-500 px-4 py-2 rounded mb-4">
          {error}
        </div>
      )}

      {isLoading ? (
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-500 border-t-transparent"></div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className='grid grid-cols-2 gap-4'>
            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">
                Operation
              </label>
              <select
                value={selectedOperation || ''}
                onChange={(e) => setSelectedOperation(e.target.value ? parseInt(e.target.value) : null)}
                className="w-full bg-black-lighter border border-black-lighter rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
              >
                <option value="">Select an operation</option>
                {operations.map((op) => (
                  <option key={op.id} value={op.id}>
                    {op.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-400 mb-1">
                Column
              </label>
              <select
                className="w-full bg-black-lighter border border-black-lighter rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
                value={fileColumn || ''}
                onChange={(e) => setFileColumn(e.target.value)}
              >
                <option value="">Select a column</option>
                {fileColumns.map((col, index) => (
                  <option key={index} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-400 mb-1">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-black-lighter border border-black-lighter rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500 max-h-[300px] min-h-[100px]"
              placeholder="Enter action description"
              rows={4}
            />
          </div>

          <button
            onClick={() => {console.log('Generate labels clicked');}}
            disabled={isLoadingSaving || !selectedOperation}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            {isLoadingSaving ? 'Generating labels...' : 'Generate labels'}
          </button>
        </div>
      )}
    </div>
  );
};
