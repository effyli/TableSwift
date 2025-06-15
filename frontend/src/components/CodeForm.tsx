import React, { useEffect, useState } from 'react';
import { Code } from '../types/code';
import { Editor } from '@monaco-editor/react';
import { Action } from '../types/action';
import { actionService } from '../services/action.service';
import { MdArrowBackIos, MdArrowForwardIos, MdOutlineSaveAs } from 'react-icons/md';
import { IoReload } from 'react-icons/io5';
import { useModal } from '../context/ModalContext';

interface CodeFormProps {
    codes: Code[];
    activeCode: number;
    isExecuted: boolean;
    onFieldChange: (field: keyof Action, value: any) => void;
    executeCode: (code: Code | undefined) => void;
}

export const CodeForm: React.FC<CodeFormProps> = ({ codes, activeCode, isExecuted, onFieldChange, executeCode }) => {
    const { handleModal, hideModal } = useModal();
    const [isSavingCode, setIsSavingCode] = useState(false);
    const [isExecutingCode, setIsExecutingCode] = useState(false);
    const [editableCode, setEditableCode] = useState<string>('');
    const [unsavedChanges, setUnsavedChanges] = useState<Record<number, string>>({});

    useEffect(() => {
        setEditableCode(unsavedChanges[activeCode] || codes[activeCode].code);
    }, [activeCode, codes]);

    const handleSwitchCode = (direction: 'prev' | 'next') => {
        setUnsavedChanges(prev => ({
            ...prev,
            [activeCode]: editableCode
        }));

        if (direction === 'prev' && activeCode > 0) {
            onFieldChange('active_code', activeCode - 1);
        } else if (direction === 'next' && activeCode < codes.length - 1) {
            onFieldChange('active_code', activeCode + 1);
        }
    };

    const handleCodeChange = (value: string | undefined) => {
        if (value !== undefined) {
            const newCode = [ ...codes ]
            newCode[activeCode] = {
                ...newCode[activeCode],
                code: value
            };

            setEditableCode(newCode[activeCode].code);
            // onFieldChange('code', newCode[activeCode]);

            setUnsavedChanges(prev => ({
                ...prev,
                [activeCode]: value
            }));
        }
    }

    const handleSavingCode = async () => {
        if (!codes?.[0]) return;
        setIsSavingCode(true);
        try {

            const newCode: Code = {
                ...codes[activeCode],
                code: editableCode
            }
            await actionService.saveCode(newCode);
            // Clear unsaved changes for this version after successful save
            setUnsavedChanges(prev => {
                const newState = { ...prev };
                delete newState[activeCode];
                return newState;
            });
        } catch (error) {
            console.error('Failed to save code:', error);
        }
        setIsSavingCode(false);
    }

    const handleExecuteCode = () => {
        setIsExecutingCode(true)
        try {
            executeCode({
                ...codes[activeCode],
                code: editableCode
            });
        } catch (error) {
            console.error('Error generating labels:', error);
        } finally {
            setIsExecutingCode(false);
            hideModal();
        }
    }

    return (
        <div className="mt-12 border-t border-gray-700 pt-12">
            <h3 className="text-lg font-semibold text-white mb-4">Code Snippets</h3>

            <Editor
                height="50vh"
                theme="vs-dark"
                defaultLanguage="python"
                value={editableCode}
                onChange={handleCodeChange}
                options={{
                    minimap: {
                        enabled: false
                    }
                }}
            />

            <div className="mt-4 flex gap-x-4 justify-between items-center">
                {
                    isExecuted ? (
                        <div className='w-full flex justify-between items-center'>
                            <div className='flex items-center'>
                                <button className='flex items-center gap-2 text-gray-400 hover:bg-black-lighter p-2 rounded-lg' onClick={() => handleSavingCode()}>
                                    <MdOutlineSaveAs />
                                </button>
                                <button 
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleModal({
                                            isOpen: true,
                                            title: 'Re-execute Action',
                                            message: 'Are you sure you want to re-execute this action? Re-executing will revert the previous execution and run the current code on the reverted data.',
                                            primaryButton: {
                                                label: 'Re-execute',
                                                onClick: () => handleExecuteCode(),
                                            },
                                            secondaryButton: {
                                                label: 'Cancel',
                                                onClick: hideModal,
                                            },
                                        })
                                    }}
                                    className='flex items-center gap-2 text-gray-400 hover:bg-black-lighter p-2 rounded-lg'
                                >
                                    <IoReload />
                                </button>
                            </div>

                            {
                                (codes.length > 1) && (
                                    <div className='flex items-center gap-2'>
                                        <button onClick={() => handleSwitchCode('prev')} disabled={activeCode === 0}>
                                            <MdArrowBackIos />
                                        </button>
                                        <span>{activeCode + 1}/{codes.length}</span>
                                        <button onClick={() => handleSwitchCode('next')} disabled={activeCode === codes.length - 1}>
                                            <MdArrowForwardIos />
                                        </button>
                                    </div>
                                )
                            }
                        </div>
                    ) : (
                        <div className='flex items-center gap-x-4'>
                            <button
                                onClick={() => handleSavingCode()}
                                disabled={isSavingCode}
                                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                            >
                                {isSavingCode ? 'Saving...' : 'Save code'}
                            </button>
                            <button
                                onClick={() => handleExecuteCode()}
                                disabled={isExecutingCode}
                                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                            >
                                {isExecutingCode ? 'Executing...' : 'Execute Code'}
                            </button>
                        </div>
                    )
                }
            </div>
        </div>
    )
}