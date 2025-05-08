import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Action, ActionUpdate } from '../types/action';
import { Operation } from '../types/operation';
import { actionService } from '../services/action.service';
import { ActionForm } from './ActionForm';

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
  const [labels, setLabels] = useState(action?.labels || {}); // TODO: Add labels state
  
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

  const generateLabels = () => {
    console.log('Generating labels...');
  }

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
        <>
          <ActionForm 
            selectedOperation={selectedOperation}
            setSelectedOperation={setSelectedOperation}
            fileColumn={fileColumn}
            setFileColumn={setFileColumn}
            description={description}
            setDescription={setDescription}
            operations={operations}
            fileColumns={fileColumns}
            isLoadingSaving={isLoadingSaving}
            error={error}
            onSave={generateLabels}
          />

          {labels && (
            <div className="mt-12 border-t border-gray-700 pt-12">
              <h3 className="text-lg font-semibold text-white">Generated Labels</h3>
              <pre className="bg-gray-800 text-gray-300 p-4 rounded">{JSON.stringify(labels, null, 2)}</pre>
            </div>
          )}
        </>
      )}
    </div>
  );
};
