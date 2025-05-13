import React, { useEffect, useState } from 'react';
import { Operation } from '../types/operation';
import { Action } from '../types/action';
import { FaRegEdit } from "react-icons/fa";
import { MdArrowBackIos, MdArrowForwardIos } from "react-icons/md";
import { Descriptions } from '../types/description';

interface ActionFormProps {
    selectedOperation: number | undefined;
    fileColumn: string | undefined;
    descriptions: Descriptions[] | undefined;
    activeDescription: number;
    setActiveDescription: (count: number) => void;
    operations: Operation[];
    fileColumns: string[];
    onFieldChange: (field: keyof Action, value: any) => void;
    generateLabels: () => void;
    error: string | null;
}

export const ActionForm: React.FC<ActionFormProps> = ({
    selectedOperation,
    fileColumn,
    descriptions,
    activeDescription,
    setActiveDescription,
    operations,
    fileColumns,
    onFieldChange,
    generateLabels,
    error,
}) => {
    const [isLoadingGenerating, setIsLoadingGenerating] = useState(false);

    useEffect(() => {
        onFieldChange('active_description', activeDescription);
    }, [activeDescription]);

    const handleGenerateLabels = () => {
        setIsLoadingGenerating(true);
        try {
            generateLabels();
        }
        catch (err) {
            console.error('Error generating labels:', err);
        } finally {
            setIsLoadingGenerating(false);
        }
    };

    return (
        <div>
            {error && (
                <div className="bg-red-900/50 border border-red-500 text-red-500 px-4 py-2 rounded mb-4">
                    {error}
                </div>
            )}

            <div className='grid grid-cols-2 gap-4 mb-4'>
                <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">
                        Operation
                    </label>
                    <select
                        className="w-full bg-black-lighter border border-black-lighter rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
                        value={selectedOperation || ''}
                        disabled={descriptions && descriptions.length > 0 && descriptions[activeDescription].id !== undefined}
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
                        className="w-full bg-black-lighter border border-black-lighter rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
                        value={fileColumn || ''}
                        disabled={descriptions && descriptions.length > 0 && descriptions[activeDescription].id !== undefined}
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
                    value={descriptions?.[activeDescription]?.description || ''}
                    disabled={descriptions && descriptions.length > 0 && descriptions[activeDescription].id !== undefined}
                    onChange={(e) => {
                        if (!descriptions) return;
                        const updatedDescriptions = [...descriptions];
                        updatedDescriptions[activeDescription] = {
                            ...updatedDescriptions[activeDescription],
                            description: e.target.value
                        };
                        onFieldChange('descriptions', updatedDescriptions);
                    }}
                    className="w-full bg-black-lighter border border-black-lighter rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500 max-h-[300px] min-h-[100px]"
                    placeholder="Enter action description"
                />
            </div>

            <div className='flex justify-between items-center px-2'>
                {descriptions && descriptions.length > 0 && descriptions[activeDescription].id !== undefined ? (
                    <>
                    <button className='flex items-center gap-2 text-gray-400 hover:text-gray-300'>
                        <FaRegEdit />
                    </button>
                    <div className='flex gap-1 text-sm'>
                        <button onClick={() => setActiveDescription(activeDescription - 1)} disabled={activeDescription === 0}>
                            <MdArrowBackIos />
                        </button>
                        <span>{activeDescription + 1}/{descriptions?.length}</span>
                        <button onClick={() => setActiveDescription(activeDescription + 1)} disabled={activeDescription === 4}>
                            <MdArrowForwardIos />
                        </button>
                    </div>
                    </>
                ) : (
                    <button
                        onClick={() => handleGenerateLabels()}
                        disabled={isLoadingGenerating || !selectedOperation}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                    >
                        {isLoadingGenerating ? 'Generating...' : 'Generate Labels'}
                    </button>
                )}
            </div>

        </div>
    );
};
