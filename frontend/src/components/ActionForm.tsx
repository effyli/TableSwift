import React, { useState } from 'react';
import { Operation } from '../types/operation';
import { Action } from '../types/action';

interface ActionFormProps {
    selectedOperation: number | null;
    fileColumn: string | undefined;
    description: string | undefined;
    operations: Operation[];
    fileColumns: string[];
    onFieldChange: (field: keyof Action, value: any) => void;
    generateLabels: () => void;
    error: string | null;
}

export const ActionForm: React.FC<ActionFormProps> = ({
    selectedOperation,
    fileColumn,
    description,
    operations,
    fileColumns,
    onFieldChange,
    generateLabels,
    error,
}) => {
    const [isLoadingGenerating, setIsLoadingGenerating] = useState(false);

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
        <div className="space-y-4">
            {error && (
                <div className="bg-red-900/50 border border-red-500 text-red-500 px-4 py-2 rounded mb-4">
                    {error}
                </div>
            )}

            <div className='grid grid-cols-2 gap-4'>
                <div>
                    <label className="block text-sm font-medium text-gray-400 mb-1">
                        Operation
                    </label>
                    <select
                        value={selectedOperation || ''}
                        onChange={(e) => {
                            const selectedOp = operations.find(op => op.id === parseInt(e.target.value));
                            onFieldChange('operation', e.target.value ? { id: parseInt(e.target.value), name: selectedOp?.name || '' } : null);
                        }}
                        className="w-full bg-black-lighter border border-black-lighter rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
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
                    value={description}
                    onChange={(e) => onFieldChange('description', e.target.value)}
                    className="w-full bg-black-lighter border border-black-lighter rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500 max-h-[300px] min-h-[100px]"
                    placeholder="Enter action description"
                    rows={4}
                />
            </div>

            <button
                onClick={() => handleGenerateLabels()}
                disabled={isLoadingGenerating || !selectedOperation}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
                {isLoadingGenerating ? 'Generating...' : 'Generate Labels'}
            </button>
        </div>
    );
};
