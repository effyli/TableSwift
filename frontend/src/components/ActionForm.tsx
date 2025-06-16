import React, { useEffect, useState, useRef } from 'react';
import { Operation } from '../types/operation';
import { Action } from '../types/action';
import { FaRegEdit } from "react-icons/fa";
import { MdArrowBackIos, MdArrowForwardIos } from "react-icons/md";
import { IoReload } from "react-icons/io5";
import { Descriptions } from '../types/description';

interface ActionFormProps {
    selectedOperation: number | undefined;
    fileColumn: string | undefined;
    descriptions: Descriptions[] | undefined;
    activeDescription: number;
    operations: Operation[];
    fileColumns: string[];
    onFieldChange: (field: keyof Action, value: any) => void;
    generateLabels: (description: string | undefined) => void;
}

export const ActionForm: React.FC<ActionFormProps> = ({
    selectedOperation,
    fileColumn,
    descriptions,
    activeDescription,
    operations,
    fileColumns,
    onFieldChange,
    generateLabels,
}) => {
    const [isLoadingGenerating, setIsLoadingGenerating] = useState(false);
    const [descriptionDisabled, setDescriptionDisabled] = useState(true);
    const [adjustedDescription, setAdjustedDescription] = useState<string | undefined>(undefined);
    const [hasDescriptions, setHasDescriptions] = useState(descriptions && descriptions.length > 0);

    const descriptionRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        // Enable description editor if there are no descriptions
        if (descriptions && descriptions.length <= 0) {
            setDescriptionDisabled(false);
        }
        if (descriptions && descriptions.length > 0) {
            setHasDescriptions(true)
        }
    }, [descriptions]);

    const openDescriptionEditor = () => {
        setAdjustedDescription(descriptions?.[activeDescription]?.description);
        setDescriptionDisabled(false);
        // Focus the textarea and move cursor to end after enabling it
        setTimeout(() => {
            const textarea = descriptionRef.current;
            if (textarea) {
                textarea.focus();
                const length = textarea.value.length;
                textarea.setSelectionRange(length, length);
            }
        }, 0);
    };

    const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setAdjustedDescription(e.target.value);
    };

    const handleSwitchDescription = (direction: 'next' | 'prev') => {
        let newActiveDescription = (direction === 'next') ? activeDescription + 1 : activeDescription - 1;
        if (newActiveDescription < 0) newActiveDescription = 0;
        if (newActiveDescription >= (descriptions ? descriptions.length : 0)) newActiveDescription = (descriptions ? descriptions.length - 1 : 0);
        onFieldChange('active_description', newActiveDescription);
    }

    const handleGenerateLabels = async () => {
        setIsLoadingGenerating(true);
        setDescriptionDisabled(true);
        try {
            await generateLabels(adjustedDescription);
        }
        catch (err) {
            alert('Error generating labels. Please try again.');
            setDescriptionDisabled(false);
        } finally {
            setIsLoadingGenerating(false);
        }
    };

    const handleRegenerateLabels = () => {
        setIsLoadingGenerating(true);
        try {
            generateLabels(undefined);
        }
        catch (err) {
            alert('Error regenerating labels. Please try again.');
        } finally {
            setIsLoadingGenerating(false);
        }
    };

    return (
        <div>
            <div className='grid grid-cols-2 gap-4 mb-4'>
                <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">
                        Operation
                    </label>
                    <select
                        className={`w-full ${hasDescriptions && descriptions![0].id !== undefined ? 'bg-black-light border border-black-light' : 'bg-black-lighter border border-black-lighter'} rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500`}
                        value={selectedOperation || ''}
                        disabled={hasDescriptions && descriptions![0].id !== undefined}
                        onChange={(e) => {
                            const selectedOp = operations.find(op => op.id === parseInt(e.target.value));
                            onFieldChange('operation', e.target.value ? { id: parseInt(e.target.value), name: selectedOp?.name || '' } : null);
                        }}
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
                        className={`w-full ${hasDescriptions && descriptions![0].id !== undefined ? 'bg-black-light border border-black-light' : 'bg-black-lighter border border-black-lighter'} rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500`}
                        value={fileColumn || ''}
                        disabled={hasDescriptions && descriptions![0].id !== undefined}
                        onChange={(e) => onFieldChange('file_column', e.target.value)}
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
                    ref={descriptionRef}
                    value={descriptionDisabled && !isLoadingGenerating ? descriptions?.[activeDescription]?.description || '' : adjustedDescription}
                    disabled={descriptionDisabled}
                    onChange={(e) => handleDescriptionChange(e)}
                    className={`w-full ${descriptionDisabled ? 'bg-black-light border border-black-light' : 'bg-black-lighter border border-black-lighter'} rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500 max-h-[300px] min-h-[100px]`}
                    placeholder="Enter action description"
                />
            </div>

            <div className='mt-1'>
                {
                isLoadingGenerating ? (
                    <div className='flex items-center'>
                        <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-500 border-t-transparent"></div>
                    </div>
                ) : descriptionDisabled ? (
                    <div className='flex justify-between items-center'>
                        <div className='flex items-center'>
                            <button className='flex items-center gap-2 text-gray-400 hover:bg-black-lighter p-2 rounded-lg' onClick={() => openDescriptionEditor()}>
                                <FaRegEdit />
                            </button>
                            <button className='flex items-center gap-2 text-gray-400 hover:bg-black-lighter p-2 rounded-lg' onClick={() => handleRegenerateLabels()}>
                                <IoReload />
                            </button>
                        </div>
                        {
                            (descriptions && descriptions.length > 1) && (
                                <div className='flex items-center gap-2'>
                                    <button onClick={() => handleSwitchDescription('prev')} disabled={activeDescription === 0}>
                                        <MdArrowBackIos />
                                    </button>
                                    <span>{activeDescription + 1}/{descriptions?.length}</span>
                                    <button onClick={() => handleSwitchDescription('next')} disabled={descriptions && activeDescription === descriptions.length - 1}>
                                        <MdArrowForwardIos />
                                    </button>
                                </div>
                            )
                        }
                    </div>
                ) : (
                    <div className='flex items-center gap-x-2'>
                        {
                            (hasDescriptions) && (
                                <button
                                    onClick={() => setDescriptionDisabled(true)}
                                    className="bg-black-lighter hover:bg-black-lightest text-white px-4 py-2 rounded-lg"
                                >
                                    Cancel
                                </button>
                            )
                        }
                        <button
                            onClick={() => handleGenerateLabels()}
                            disabled={isLoadingGenerating || !selectedOperation || !fileColumn || !adjustedDescription}
                            className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                        >
                            {isLoadingGenerating ? 'Generating...' : hasDescriptions ? 'Regenerate Labels' : 'Generate Labels'}
                        </button>
                    </div>
                )}
            </div>

        </div>
    );
};
