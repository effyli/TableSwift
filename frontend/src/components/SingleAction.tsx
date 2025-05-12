import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Action } from '../types/action';
import { Operation } from '../types/operation';
import { actionService } from '../services/action.service';
import { ActionForm } from './ActionForm';
import { LabelForm } from './LabelForm';

interface SingleActionProps {
    projectAction: Action | null | undefined;
    onActionUpdate: (action: Action | null) => void;
    operations: Operation[];
    fileColumns: string[];
}

export const SingleAction: React.FC<SingleActionProps> = ({ projectAction, onActionUpdate, operations, fileColumns }) => {
  const { projectId, actionId } = useParams();
  const navigate = useNavigate();

  const [action, setAction] = useState<Action | null>(projectAction || null);

  // const [selectedOperation, setSelectedOperation] = useState<number | null>(action?.operation?.id || null);
  // const [fileColumn, setFileColumn] = useState<string | undefined>(action?.file_column || undefined);
  // const [description, setDescription] = useState<string | undefined>(action?.description || undefined);
  // const [labels, setLabels] = useState<JSON[] | undefined>(action?.labels || undefined); 
  // const [code, setCode] = useState<string[] | undefined>(action?.code || undefined);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isLoadingSaving, setIsLoadingSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Load the action only when needed
    if ((!action && actionId) || (action && action.id !== parseInt(actionId ?? ''))) {
      onActionUpdate(null);
      setIsLoading(true);
      
      actionService.getAction(parseInt(actionId!)).then((actionData) => {
        // onActionUpdate(actionData);
        setAction(actionData);
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
  
  // // Update all form fields when action changes 
  // useEffect(() => {
  //   if (projectAction) {
  //     setAction(projectAction);
  //     // setSelectedOperation(action.operation?.id || null);
  //     // setFileColumn(action.file_column);
  //     // setDescription(action.description);
  //     // setLabels(action.labels);
  //     // setCode(action.code);
  //   } else {
  //     // Reset form if action is null
  //     setAction(null);
  //     // setSelectedOperation(null);
  //     // setFileColumn(undefined);
  //     // setDescription(undefined);
  //     // setLabels(undefined);
  //     // setCode(undefined);
  //   }
  // }, [projectAction]);

  const handleBack = () => {
    if (projectId) {
      navigate(`/dashboard/${projectId}`);
    }
  };

  const handleActionChange = (field: keyof Action, value: any) => {
    if (!action || !(field in action)) return; // TODO reload page
    setAction({
      ...action,
      [field]: value
    } as Action);
  }

  // const makeAction = () => {
  //   if (!action || !actionId) return;

  //   return {
  //       id: parseInt(actionId),
  //       project_id: projectId!,
  //       datetime: action.datetime,
  //       operation: { id: selectedOperation, name: '' },
  //       file_column: fileColumn,
  //       description: description,
  //       labels: labels,
  //       code: code,
  //     };
  // };

  // Handle save action
  const handleSave = async () => {
    setIsLoadingSaving(true);

    try {
      if (!action) {
        setError('Please fill in all fields');
        return;
      }

      const updatedAction = await actionService.updateAction(action);
      onActionUpdate(updatedAction);
    } catch (error) {
      setError('Failed to save action');
      console.error('Error saving action:', error);
    } finally {
      setIsLoadingSaving(false);
    }
  };

  // Handle generate labels
  const generateLabels = async () => {
    console.log('Generating labels...');
    setIsLoadingSaving(true);

    try {
      if (!action) {
        setError('Please fill in all fields');
        return;
      }

      const updatedAction = await actionService.generateLabels(action);
      onActionUpdate(updatedAction);
    } catch (error) {
      setError('Failed to save action');
      console.error('Error saving action:', error);
    } finally {
      setIsLoadingSaving(false);
    }
  }

  // Handle generate code
  const generateCode = async () => {
    console.log('Generating code...');  
    setIsLoadingSaving(true);

    try {
      if (!action) {
        setError('Please fill in all fields');
        return;
      }

      const updatedAction = await actionService.generateCode(action);
      onActionUpdate(updatedAction);
    } catch (error) {
      setError('Failed to save action');
      console.error('Error saving action:', error);
    } finally {
      setIsLoadingSaving(false);
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
            disabled={isLoadingSaving || !action?.operation?.id}
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
          {action && (
            <>
              <ActionForm 
                selectedOperation={action.operation?.id || null}
                fileColumn={action.file_column}
                description={action.description}
                operations={operations}
                fileColumns={fileColumns}
                onFieldChange={handleActionChange}
                generateLabels={generateLabels}
                error={error}
              />

              {action.labels && (
          <LabelForm labels={action.labels} generateCode={generateCode} />
              )}
            </>
          )}
        </>
      )}
    </div>
  );
};
