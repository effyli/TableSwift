import React, { useEffect, useState } from 'react';
import { Code } from '../types/code';
import { Editor } from '@monaco-editor/react';
import { Action } from '../types/action';
import { actionService } from '../services/action.service';
import { MdArrowBackIos, MdArrowForwardIos } from 'react-icons/md';
import { IoReload } from 'react-icons/io5';

interface CodeFormProps {
    codes: Code[];
    activeCode: number;
    onFieldChange: (field: keyof Action, value: any) => void;
}


export const CodeForm: React.FC<CodeFormProps> = ({ codes, activeCode, onFieldChange }) => {

    const [isSavingCode, setIsSavingCode] = useState(false);
    const [isExecutingCode, setIsExecutingCode] = useState(false);
    const [editableCode, setEditableCode] = useState<string>('');

    useEffect(() => {
        setEditableCode(codes[activeCode].code);
    }
    , [activeCode]);

    const handleSwitchCode = (direction: 'prev' | 'next') => {
        if (direction === 'prev' && activeCode > 0) {
            onFieldChange('active_code', activeCode - 1);
        } else if (direction === 'next' && activeCode < codes.length - 1) {
            // Switch to the next code
            onFieldChange('active_code', activeCode + 1);
        }
    };

    const handleCodeChange = (value: string | undefined) => {
        if (value !== undefined) {
            setEditableCode(value);
        }
    }

    const handleSavingCode = async () => {
        setIsSavingCode(true)
        console.log("Saving code:", editableCode);
        const result = await actionService.saveCode({
            ...codes[activeCode],
            code: editableCode
        });
        console.log("Code saved:", result);
        setIsSavingCode(false);
    }

    const handleExecuteCode = () => {
        setIsExecutingCode(true)
        const codeToExecute = editableCode;
        console.log("Executing code:", codeToExecute);
        setTimeout(() => {
            setIsExecutingCode(false);
        }, 3000);
    }

    return (
        <div className="mt-12 border-t border-gray-700 pt-12">
            <h3 className="text-lg font-semibold text-white mb-4">Code Snippets</h3>

            <Editor 
            height="50vh" 
            theme="vs-dark" 
            defaultLanguage="python" 
            defaultValue={editableCode}
            onChange={handleCodeChange}
            options={{
                minimap: {
                    enabled: false
                }
            }}
            />

            <div className="mt-4 flex gap-x-4 justify-between items-center">
                {
                    false ? (
                        <div className='flex items-center'>
                            <button className='flex items-center gap-2 text-gray-400 hover:bg-black-lighter p-2 rounded-lg' onClick={() => handleExecuteCode()}>
                                <IoReload />
                            </button>
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
        </div>
    )
}