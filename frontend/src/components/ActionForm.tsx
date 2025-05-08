import React from 'react';
import { Operation } from '../types/operation';

interface ActionFormProps {
    selectedOperation: number | null;
    setSelectedOperation: (operation: number | null) => void;
    fileColumn: string;
    setFileColumn: (column: string) => void;
    description: string;
    setDescription: (description: string) => void;
    operations: Operation[];
    fileColumns: string[];
    isLoadingSaving: boolean;
    error: string | null;
    onSave: () => void;
}

export const ActionForm: React.FC<ActionFormProps> = ({
    selectedOperation,
    setSelectedOperation,
    fileColumn,
    setFileColumn,
    description,
    setDescription,
    operations,
    fileColumns,
    isLoadingSaving,
    error,
    onSave,
}) => {
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
                        onChange={(e) => setSelectedOperation(e.target.value ? parseInt(e.target.value) : null)}
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
                        onChange={(e) => setFileColumn(e.target.value)}
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
                    onChange={(e) => setDescription(e.target.value)}
                    className="w-full bg-black-lighter border border-black-lighter rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500 max-h-[300px] min-h-[100px]"
                    placeholder="Enter action description"
                    rows={4}
                />
            </div>

            <button
                onClick={onSave}
                disabled={isLoadingSaving || !selectedOperation}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
                {isLoadingSaving ? 'Saving...' : 'Generate Labels'}
            </button>
        </div>
    );
};
