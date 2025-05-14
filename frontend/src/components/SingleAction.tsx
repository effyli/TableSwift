import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Action } from '../types/action';
import { Operation } from '../types/operation';
import { actionService } from '../services/action.service';
import { ActionForm } from './ActionForm';
import { LabelForm } from './LabelForm';
import { formatActionJson } from '../util/formatAction';

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
  const containerRef = useRef<HTMLDivElement>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
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

  useEffect(() => {
    // Remove error message after 5 seconds
    if (error) {
      setTimeout(() => {
        setError(null);
      }, 5000);
    }
  }, [error]);
  
  const handleBack = () => {
    if (projectId) {
      navigate(`/dashboard/${projectId}`);
    }
  };

  const handleActionChange = (field: keyof Action, value: any) => {
    if (!projectAction || !(field in projectAction)) return; // TODO reload page?

    if (field === 'active_description') {
      projectAction.active_labels = projectAction.descriptions[value]!.labels!.length - 1
    }

    onActionUpdate({
      ...projectAction,
      [field]: value
    } as Action);
  }

  const scrollToBottom = () => {
    if (containerRef.current) {
      setTimeout(() => {
        containerRef.current?.scrollTo({
          top: containerRef.current.scrollHeight,
          behavior: 'smooth'
        });
      }, 100); // Small delay to ensure content is rendered
    }
  };

  // Handle generate labels
  const generateLabels = async (description: string | undefined) => {
    setError(null);
    console.log('Generating labels for action:', projectAction);
    if (!projectAction || !projectAction.operation?.id || !projectAction.file_column || (!description && projectAction.descriptions?.length === 0)) {
      setError('Please fill in all fields');
      throw new Error('Please fill in all fields');
    }

    try { 
      // Make a copy of action to avoid mutating the original object
      if (description) {
        projectAction.descriptions.push({ description: description })
        projectAction.active_description = projectAction.descriptions.length - 1;
      }
      const formattedAction = formatActionJson(JSON.parse(JSON.stringify(projectAction)));
      const updatedDescription = await actionService.generateLabels(formattedAction);
        // Add the generated labels in the active description of the action
        const updatedDescriptions = [...(projectAction.descriptions || [])];
        updatedDescriptions[projectAction.active_description] = updatedDescription;
        const updatedAction = {
          ...formattedAction,
          active_labels: updatedDescription.labels ? updatedDescription.labels.length - 1 : 0,
          descriptions: updatedDescriptions
        };
        console.log('Updated action:', updatedAction);
        onActionUpdate(updatedAction);
        scrollToBottom();

    } catch (error) {
      setError('Failed to save action');
      throw new Error('Failed to save action');
    }
  }

  // Handle generate code
  const generateCode = async () => {
    if (!projectAction) {
      setError('Please fill in all fields');
      return;
    }

    try {
      const formattedAction = formatActionJson({ ...projectAction });
      const code = await actionService.generateCode(formattedAction);
      console.log('Generated code:', code);
      scrollToBottom();
    } catch (error) {
      setError('Failed to save action');
      console.error('Error saving action:', error);
    }
  };

  return (
    <div ref={containerRef} className="bg-black border-r border-black-lighter p-8 pb-24 pt-0 h-full flex flex-col overflow-auto custom-scrollbar">
      <div className="bg-black sticky top-0 py-4 flex flex-col gap-y-4">
        <div className='flex items-center justify-between'>
          <button
            onClick={handleBack}
            className="text-indigo-500 hover:text-indigo-400 mr-4"
          >
            ← Back to Actions
          </button>
        </div>

        {error && (
          <div className="bg-red-900/50 border border-red-500 text-red-500 px-4 py-2 rounded mb-4">
            {error}
          </div>
        )}
      </div>


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
              />

              {projectAction.descriptions?.[projectAction.active_description]?.labels && (
                <LabelForm
                  labels={projectAction.descriptions[projectAction.active_description].labels!}
                  activeLabels={projectAction.active_labels}
                  selectedOperation={projectAction.operation}
                  generateCode={generateCode}
                  onFieldChange={handleActionChange}
                />
              )}
            </>
          )}
        </>
      )}
    </div>
  );
};
