import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Action } from '../types/action';
import { Operation } from '../types/operation';
import { Labels } from '../types/labels';
import { Code } from '../types/code';
import { File } from '../types/file';
import { actionService } from '../services/action.service';
import { ActionForm } from './ActionForm';
import { LabelForm } from './LabelForm';
import { CodeForm } from './CodeForm';
import { formatActionJson } from '../util/formatAction';
import { DiffViewer } from './Diff';

interface SingleActionProps {
    projectAction: Action | null | undefined;
    isLoadingProject: boolean;
    onActionUpdate: (action: Action | null) => void;
    handleFileDataUpdate: (file: File) => void;
    operations: Operation[];
    fileColumns: string[];
}

export const SingleAction: React.FC<SingleActionProps> = ({ projectAction, isLoadingProject, onActionUpdate, handleFileDataUpdate, operations, fileColumns }) => {
  const { projectId, actionId } = useParams();
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [showAffectedRows, setShowAffectedRows] = useState<boolean>(false);

  useEffect(() => {
    scrollToBottom();
  }, []);

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
      const newDescription = projectAction.descriptions[value];
      // Set to the last label in the new description
      projectAction.active_labels = newDescription?.labels?.length ? newDescription.labels.length - 1 : 0;
      // Set to the last code in the selected label
      projectAction.active_code = newDescription?.labels?.[projectAction.active_labels]?.codes?.length ? 
        newDescription.labels[projectAction.active_labels].codes.length - 1 : 0;
    }

    if (field === 'active_labels') {
      const newLabel = projectAction.descriptions[projectAction.active_description]?.labels?.[value];
      projectAction.active_code = newLabel?.codes?.length ? newLabel.codes.length - 1 : 0;
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
      }, 150); // Small delay to ensure content is rendered
    }
  };

  // Handle generate labels
  const generateLabels = async (description: string | undefined) => {
    setError(null);
    if (!projectAction || !projectAction.operation?.id || !projectAction.file_column || (!description && projectAction.descriptions?.length === 0)) {
      setError('Please fill in all fields');
      throw new Error('Please fill in all fields');
    }

    try { 
      if (description) {
        projectAction.descriptions.push({ description: description })
        projectAction.active_description = projectAction.descriptions.length - 1;
      }
      // Make a copy of action to avoid mutating the original object
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
        onActionUpdate(updatedAction);
        scrollToBottom();

    } catch (error) {
      setError('Failed to save action');
      throw new Error('Failed to save action');
    }
  }

  // Handle generate code
  const generateCode = async (labels: Labels | undefined) => {
    if (!projectAction) {
      setError('Please fill in all fields');
      return;
    }

    try {
      if (labels) {
        // If labels are provided, update the active labels
        projectAction.descriptions[projectAction.active_description].labels![projectAction.active_labels] = labels;
      }
      const formattedAction = formatActionJson(JSON.parse(JSON.stringify(projectAction)));
      const codeResult = await actionService.generateCode(formattedAction);

      const updatedDescriptions = [...projectAction.descriptions];
      const activeDescription = updatedDescriptions[projectAction.active_description];
      const activeLabel = activeDescription.labels![projectAction.active_labels];
      activeLabel.codes.push(codeResult);

      onActionUpdate({
        ...projectAction,
        active_code: activeLabel.codes.length - 1,
        descriptions: updatedDescriptions
      });

      scrollToBottom();
    } catch (error) {
      setError('Failed to save action');
      console.error('Error saving action:', error);
    }
  };

  const executeCode = async (code: Code | undefined) => {
    if (!projectAction) {
      setError('Please fill in all fields');
      return;
    }

    try {
      if (code) {
        // If code is provided, update the active code
        projectAction.descriptions[projectAction.active_description].labels![projectAction.active_labels].codes![projectAction.active_code] = code;
      }
      const formattedAction = formatActionJson(JSON.parse(JSON.stringify(projectAction)));
      const result = await actionService.executeCode(formattedAction);
      handleFileDataUpdate(result);
    } catch (error) {
      setError('Failed to execute code');
      console.error('Error executing code:', error);
    }
  }

  return (
    <div ref={containerRef} className="bg-black border-r border-black-lighter p-8 pb-24 pt-0 h-full flex flex-col overflow-auto custom-scrollbar">
      <div className="bg-black sticky top-0 py-4 flex flex-col gap-y-4 z-100">
        <div className='flex items-center justify-between'>
          <button
            onClick={handleBack}
            className="text-indigo-500 hover:text-indigo-400 mr-4"
          >
            ← Back to Actions
          </button>

          {projectAction && projectAction.file && (
            <div className='justify-self-end'>
              <button
                onClick={() => setShowAffectedRows(!showAffectedRows)}
                className="min-w-[100px] px-4 py-2 bg-indigo-600 text-white rounded-lg
                    transition-colors flex items-center justify-center gap-2 hover:bg-indigo-700"
              >
                {showAffectedRows ? 'Show Action' : 'Show Affected Rows'}
              </button>
            </div>
          )}
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
          {projectAction && (projectAction.file && showAffectedRows ? (
            <>
              <DiffViewer 
                action={projectAction}
                file={projectAction.file}
                handleActionChange={handleActionChange}
              />
            </>
          ) : (
            <>
              <ActionForm
                selectedOperation={projectAction.operation?.id}
                fileColumn={projectAction.file_column}
                descriptions={projectAction.descriptions || []}
                activeDescription={projectAction?.active_description || 0}
                operations={operations}
                fileColumns={fileColumns}
                onFieldChange={handleActionChange}
                generateLabels={generateLabels}
              />

              {projectAction?.descriptions?.[projectAction.active_description]?.labels && (
                <>
                  <LabelForm
                    labels={projectAction?.descriptions[projectAction.active_description]?.labels || []}
                    activeLabels={projectAction?.active_labels || 0}
                    selectedOperation={projectAction?.operation}
                    generateCode={generateCode}
                    onFieldChange={handleActionChange}
                  />

                  {projectAction.descriptions[projectAction.active_description].labels![projectAction.active_labels]!.codes!.length > 0 && (
                  <CodeForm 
                    codes={projectAction?.descriptions[projectAction.active_description]?.labels?.[projectAction.active_labels]?.codes || []} 
                    activeCode={projectAction?.active_code || 0}
                    isExecuted={!!projectAction?.file}
                    onFieldChange={handleActionChange}
                    executeCode={executeCode}
                  />
                  )}
                </>
              )}
            </>
          ))}
        </>
      )}
    </div>
  );
};
