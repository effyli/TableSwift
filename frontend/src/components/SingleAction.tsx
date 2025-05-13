import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Action } from '../types/action';
import { Operation } from '../types/operation';
import { actionService } from '../services/action.service';
import { ActionForm } from './ActionForm';
import { LabelForm } from './LabelForm';
import { formatLabelsJson } from '../util/formatAction';

interface SingleActionProps {
    projectAction: Action | null | undefined;
    isLoadingProject: boolean;
    onActionUpdate: (action: Action | null) => void;
    activeDescription: number;
    setActiveDescription: (count: number) => void;
    operations: Operation[];
    fileColumns: string[];
}

export const SingleAction: React.FC<SingleActionProps> = ({ projectAction, isLoadingProject, onActionUpdate, operations, fileColumns, activeDescription, setActiveDescription }) => {
  const { projectId, actionId } = useParams();
  const navigate = useNavigate();

  const [action, setAction] = useState<Action | null>(projectAction || null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isLoadingSaving, setIsLoadingSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('Project action:', projectAction);
    setAction(projectAction || null);
    setIsLoading(false);
  }, [projectAction]);

  useEffect(() => {
    // Load the action only when not loaded by the full project in dashboard
    if ((!action && actionId && !isLoadingProject) || (action && action.id !== parseInt(actionId ?? '') && !isLoadingProject)) {
      setIsLoading(true);
      onActionUpdate(null);
      
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
  
  const handleBack = () => {
    if (projectId) {
      navigate(`/dashboard/${projectId}`);
    }
  };

  const handleActionChange = (field: keyof Action, value: any) => {
    if (!action || !(field in action)) return; // TODO reload page?

    onActionUpdate({
      ...action,
      [field]: value
    } as Action);
  }

  // Handle save action
  const handleSave = async () => {
    setIsLoadingSaving(true);
    if (!action) {
      setError('Please fill in all fields');
      return;
    }

    try {
      // Make a copy of action to avoid mutating the original object
      const formattedAction = formatLabelsJson({ ...action });
      console.log('Saving action:', formattedAction);
      const updatedAction = await actionService.updateAction(formattedAction);
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
    setIsLoadingSaving(true);
    if (!action) {
      setError('Please fill in all fields');
      return;
    }

    try { 
      // Make a copy of action to avoid mutating the original object
      const formattedAction = formatLabelsJson({ ...action });
      const labels = await actionService.generateLabels(formatLabelsJson(formattedAction));

      const updatedDescriptions = [...(action.descriptions || [])];
      updatedDescriptions[activeDescription] = {
        ...updatedDescriptions[activeDescription],
        version: action.descriptions?.length || 0,
        labels: labels
      };

      const updatedAction = {
        ...formattedAction,
        descriptions: updatedDescriptions
      };
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
    setIsLoadingSaving(true);
    if (!action) {
      setError('Please fill in all fields');
      return;
    }

    try {
      // Make a copy of action to avoid mutating the original object
      const formattedAction = formatLabelsJson({ ...action });
      const code = await actionService.generateCode(formattedAction);
    } catch (error) {
      setError('Failed to save action');
      console.error('Error saving action:', error);
    } finally {
      setIsLoadingSaving(false);
    }
  };

  return (
    <div className="bg-black-light border-r border-black-lighter p-8 pb-24 pt-0 h-full flex flex-col overflow-auto custom-scrollbar">
      <div className="bg-black-light sticky top-0 flex items-center justify-between py-4">
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
                selectedOperation={action.operation?.id || undefined}
                fileColumn={action.file_column}
                descriptions={action.descriptions}
                activeDescription={activeDescription}
                setActiveDescription={setActiveDescription}
                operations={operations}
                fileColumns={fileColumns}
                onFieldChange={handleActionChange}
                generateLabels={generateLabels}
                error={error}
              />

              {action.descriptions?.[activeDescription]?.labels && (
                <LabelForm
                  labels={action.descriptions?.[activeDescription].labels}
                  generateCode={generateCode}
                />
              )}
            </>
          )}
        </>
      )}
    </div>
  );
};
