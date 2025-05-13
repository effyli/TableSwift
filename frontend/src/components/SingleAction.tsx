import React, { useState, useEffect, use } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Action } from '../types/action';
import { Operation } from '../types/operation';
import { actionService } from '../services/action.service';
import { ActionForm } from './ActionForm';
import { LabelForm } from './LabelForm';
import { formatActionJson, parseLabels } from '../util/formatAction';

interface SingleActionProps {
    projectAction: Action | null | undefined;
    isLoadingProject: boolean;
    onActionUpdate: (action: Action | null) => void;
    operations: Operation[];
    fileColumns: string[];
}

export const SingleAction: React.FC<SingleActionProps> = ({ projectAction, isLoadingProject, onActionUpdate, operations, fileColumns }) => {
  const { projectId, actionId } = useParams();
  const navigate = useNavigate();

  const [isLoading, setIsLoading] = useState<boolean>(true);
  // const [isLoadingSaving, setIsLoadingSaving] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('Project action updated:', projectAction);
  }, [projectAction]);

  useEffect(() => {
    // Load the action only when not loaded by the full project in dashboard
    if ((!projectAction && actionId && !isLoadingProject) || (projectAction && actionId && projectAction.id !== parseInt(actionId) && !isLoadingProject)) {
      setIsLoading(true);
      onActionUpdate(null);
      
      actionService.getAction(parseInt(actionId)).then((actionData) => {
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
    if (!projectAction || !(field in projectAction)) return; // TODO reload page?

    onActionUpdate({
      ...projectAction,
      [field]: value
    } as Action);
  }

  // // Handle save action
  // const handleSave = async () => {
  //   setIsLoadingSaving(true);
  //   if (!projectAction) {
  //     setError('Please fill in all fields');
  //     return;
  //   }

  //   try {
  //     // Make a copy of action to avoid mutating the original object
  //     const formattedAction = formatActionJson({ ...projectAction });
  //     const updatedAction = await actionService.updateAction(formattedAction);
  //     onActionUpdate(updatedAction);
  //   } catch (error) {
  //     setError('Failed to save action');
  //     console.error('Error saving action:', error);
  //   } finally {
  //     setIsLoadingSaving(false);
  //   }
  // };

  // Handle generate labels
  const generateLabels = async (description: string | undefined) => {
    if (!projectAction) {
      setError('Please fill in all fields');
      return;
    }

    try { 
      // Make a copy of action to avoid mutating the original object
      if (description) {
        projectAction.descriptions.push({ description: description })
        projectAction.active_description = projectAction.descriptions.length - 1;
      }
      console.log('Project action before generating labels:', projectAction);
      const formattedAction = formatActionJson(JSON.parse(JSON.stringify(projectAction)));
      console.log('Formatted action for label generation:', formattedAction);
      const labels = await actionService.generateLabels(formattedAction);
      console.log('Generated labels:', labels);
        // Add the generated labels in the active description of the action
        const updatedDescriptions = [...(projectAction.descriptions || [])];
        updatedDescriptions[projectAction.active_description] = {
          ...updatedDescriptions[projectAction.active_description],
          version: projectAction.descriptions?.length || 0,
          labels: [...(updatedDescriptions[projectAction.active_description].labels || []), labels]
        };
        console.log('Updated descriptions:', updatedDescriptions);
        const updatedAction = {
          ...formattedAction,
          descriptions: updatedDescriptions
        };
        console.log('Updated action:', updatedAction);
  
        onActionUpdate(updatedAction);

    } catch (error) {
      setError('Failed to save action');
      console.error('Error saving action:', error);
    }
  }

  // Handle generate code
  const generateCode = async () => {
    if (!projectAction) {
      setError('Please fill in all fields');
      return;
    }

    try {
      // Make a copy of action to avoid mutating the original object
      const formattedAction = formatActionJson({ ...projectAction });
      const code = await actionService.generateCode(formattedAction);
    } catch (error) {
      setError('Failed to save action');
      console.error('Error saving action:', error);
    }
  };

  return (
    <div className="bg-black border-r border-black-lighter p-8 pb-24 pt-0 h-full flex flex-col overflow-auto custom-scrollbar">
      <div className="bg-black sticky top-0 flex items-center justify-between py-4">
        <button
          onClick={handleBack}
          className="text-indigo-500 hover:text-indigo-400 mr-4"
        >
          ← Back to Actions
        </button>
        {/* {!isLoading && (
          <button
            onClick={handleSave}
            disabled={isLoadingSaving || !projectAction?.operation?.id}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
          >
            {isLoadingSaving ? 'Saving...' : 'Save Action'}
          </button>  
        )} */}
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
          {projectAction && (
            <>
              <ActionForm
                selectedOperation={projectAction.operation?.id || undefined}
                fileColumn={projectAction.file_column}
                descriptions={projectAction.descriptions}
                activeDescription={projectAction.active_description}
                operations={operations}
                fileColumns={fileColumns}
                onFieldChange={handleActionChange}
                generateLabels={generateLabels}
                error={error}
              />

              {projectAction.descriptions?.[projectAction.active_description]?.labels && (
                <LabelForm
                  labels={projectAction.descriptions?.[projectAction.active_description]?.labels}
                  generateCode={generateCode}
                  selectedOperation={projectAction.operation}
                />
              )}
            </>
          )}
        </>
      )}
    </div>
  );
};
