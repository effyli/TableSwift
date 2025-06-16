import React, { useEffect, useState } from 'react';
import { Labels } from '../types/labels';
import { Operation } from '../types/operation';
import { actionService } from '../services/action.service'
import { MdArrowBackIos, MdArrowForwardIos, MdOutlineSaveAs } from 'react-icons/md';
import { Action } from '../types/action';
import { IoReload } from 'react-icons/io5';

interface LabelFormProps {
    labels: Labels[];
    activeLabels: number;
    selectedOperation?: Operation;
    generateCode: (labels: Labels | undefined) => void;
    onFieldChange: (field: keyof Action, value: any) => void;
}

interface LabelRow {
    [key: string]: string;
}

type LabelPair = [LabelRow, LabelRow, { feedback?: 'good' | 'wrong' }];

interface SourceDataRow extends LabelRow {
    Label: string;
}

export const LabelForm: React.FC<LabelFormProps> = ({ labels, activeLabels, selectedOperation, generateCode, onFieldChange }) => {
    const [isLoadingGenerating, setIsLoadingGenerating] = useState(false);
    const [isSavingLabels, setIsSavingLabels] = useState(false);
    const [editableLabels, setEditableLabels] = useState<LabelPair[]>([]);

    useEffect(() => {
        if (labels?.[0]?.json) {
            // Convert existing labels to new format if they don't have feedback
            const labelsWithFeedback = (labels[activeLabels].json as any[]).map(pair => {
                if (pair.length === 2) {
                    return [...pair, { feedback: undefined }] as LabelPair;
                }
                return pair as LabelPair;
            });
            setEditableLabels(labelsWithFeedback);
        }
    }, [labels]);

    const handleFeedback = (rowIndex: number, feedback: 'good' | 'wrong') => {
        const newLabels = [...editableLabels];
        newLabels[rowIndex][2] = { 
            feedback: newLabels[rowIndex][2]?.feedback === feedback ? undefined : feedback 
        };
        setEditableLabels(newLabels);
    };

    const handleSwitchLabels = (direction: 'next' | 'prev') => {
        activeLabels = (direction == 'next') ? activeLabels + 1 : activeLabels - 1;
        if (activeLabels < 0) activeLabels = 0;
        if (activeLabels >= labels.length) activeLabels = labels.length - 1;
        onFieldChange('active_labels', activeLabels);
        setEditableLabels(labels[activeLabels].json as LabelPair[]);
    };

    const handleSavingLabels = async () => {
        if (!labels?.[0]) return;
        setIsSavingLabels(true);

        const newLabels: Labels = {
            ...labels[activeLabels],
            json: JSON.stringify(editableLabels)
        };

        try {
            await actionService.saveLabels(newLabels);
            // TODO success message
        } catch (error) {
            console.error('Error saving labels:', error);
        } finally {
            setIsSavingLabels(false);
        }
    }

    const handleGenerateCode = () => {
        setIsLoadingGenerating(true);
        try {
            generateCode({
                ...labels[activeLabels],
                json: editableLabels
            });
        } catch (error) {
            console.error('Error generating labels:', error);
        } finally {
            setIsLoadingGenerating(false);
        }
    };

    const handleLabelChange = (rowIndex: number, value: string) => {
        const newLabels = [...editableLabels];
        newLabels[rowIndex][1].Label = value;
        setEditableLabels(newLabels);
    };

    const isEntityMatching = selectedOperation?.id === 4;
    let table = null;

    if (isEntityMatching) {
        // Entity Matching View - Show items as rows under each other
        table = (
            <div className="space-y-8">
                {(editableLabels).map((row, rowIndex) => (
                    <div key={rowIndex} className="border border-gray-700 rounded-lg overflow-hidden">
                        <table className="min-w-full divide-y divide-gray-700">
                            <thead className="bg-black-lighter">
                                <tr>
                                    {Object.keys(row[0]).map((header, i) => (
                                        <th key={i} className="px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                                            {header}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody className="bg-black-light divide-y divide-gray-700">
                                {[row[0], row[1]].map((item, itemIndex) => (
                                    <tr key={itemIndex} className="h-[60px]">
                                        {Object.values(item).map((value, colIndex) => (
                                            <td key={colIndex} className="px-4 py-3 text-sm text-white align-middle">
                                                {value}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        <div className="bg-black-lighter px-4 py-3 flex justify-end gap-x-2 border-t border-gray-700">
                            <button
                                onClick={() => handleFeedback(rowIndex, 'good')}
                                className={`px-4 py-2 rounded-lg transition-colors ${
                                    row[2]?.feedback === 'good'
                                        ? 'bg-green-600 text-white'
                                        : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                                }`}
                            >
                                Good
                            </button>
                            <button
                                onClick={() => handleFeedback(rowIndex, 'wrong')}
                                className={`px-4 py-2 rounded-lg transition-colors ${
                                    row[2]?.feedback === 'wrong'
                                        ? 'bg-red-600 text-white'
                                        : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                                }`}
                            >
                                Wrong
                            </button>
                        </div>
                    </div>
                ))}
            </div>
        );
    } else {
        // Regular View - Single table with sticky label column
        const sourceData: SourceDataRow[] = (labels[activeLabels].json as LabelPair[]).map(row => ({
            ...row[0],
            Label: row[1].Label
        }));
        const headers = [...Object.keys(labels[activeLabels].json[0][0]), 'Label'];
    
        table = (                
            <div className="border border-gray-700 rounded-lg overflow-hidden">
                <div className="overflow-x-auto custom-scrollbar">
                    <table className="min-w-full border-separate border-spacing-0">
                        <thead>
                            <tr className="bg-black-lighter">
                                {headers.map((header, i) => (
                                    <th 
                                        key={i} 
                                        className={`px-4 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider whitespace-nowrap border-gray-700 ${
                                            header === 'Label' ? 'sticky right-0 min-w-[150px] border-l-1 border-grey bg-black-lighter shadow-[-4px_0_8px_-4px_rgba(0,0,0,0.3)]' : ''
                                        }`}
                                    >
                                        {header}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody className="bg-black-light">
                            {sourceData.map((row, rowIndex) => (
                                <tr key={rowIndex} className="h-[60px]">
                                    {headers.map((header, colIndex) => (
                                        <td 
                                            key={colIndex} 
                                            className={`px-4 py-3 text-sm align-middle whitespace-nowrap border-gray-700 ${
                                                header === 'Label' 
                                                    ? 'sticky right-0 border-l-1 border-grey bg-black-light shadow-[-4px_0_8px_-4px_rgba(0,0,0,0.3)]' 
                                                    : 'text-white'
                                            }`}
                                        >
                                            {header === 'Label' ? (
                                                <input
                                                    type="text"
                                                    value={row[header]}
                                                    onChange={(e) => handleLabelChange(rowIndex, e.target.value)}
                                                    className="w-full bg-black-lighter border border-gray-700 rounded px-2 py-1 text-white focus:outline-none focus:border-indigo-500"
                                                />
                                            ) : (
                                                row[header]
                                            )}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        );
    }


    return (
        <div className="mt-12 border-t border-gray-700 pt-12">
                <h3 className="text-lg font-semibold text-white mb-4">Generated Labels</h3>
                
                {table}
                <div className="mt-4 flex gap-x-4 justify-between items-center">
                    {
                        isLoadingGenerating ? (
                            <div className='flex items-center justify-center'>
                                <div className="animate-spin rounded-full h-8 w-8 border-2 border-indigo-500 border-t-transparent"></div>
                            </div>
                        ) : labels[activeLabels].codes && labels[activeLabels].codes.length > 0 ? (
                            <div className='w-full flex justify-between items-center'>
                                <div className='flex items-center'>
                                    <button className='flex items-center gap-2 text-gray-400 hover:bg-black-lighter p-2 rounded-lg' onClick={() => handleSavingLabels()}>
                                        <MdOutlineSaveAs />
                                    </button>
                                    <button className='flex items-center gap-2 text-gray-400 hover:bg-black-lighter p-2 rounded-lg' onClick={() => handleGenerateCode()}>
                                        <IoReload />
                                    </button>
                                </div>
                            </div>
                        ) : (
                            <div className='flex items-center gap-x-4'>
                                <button
                                    onClick={() => handleSavingLabels()}
                                    disabled={isSavingLabels}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                                >
                                    {isSavingLabels ? 'Saving...' : 'Save labels'}
                                </button>
                                <button
                                    onClick={() => handleGenerateCode()}
                                    disabled={isLoadingGenerating}
                                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
                                >
                                    {isLoadingGenerating ? 'Generating...' : 'Generate Code'}
                                </button>
                            </div>
                        )
                    }
                    {
                        (labels && labels.length > 1) && (
                            <div className='flex items-center gap-2'>
                                <button onClick={() => handleSwitchLabels('prev')} disabled={activeLabels === 0}>
                                    <MdArrowBackIos />
                                </button>
                                <span>{activeLabels + 1}/{labels?.length}</span>
                                <button onClick={() => handleSwitchLabels('next')} disabled={labels && activeLabels === labels.length - 1}>
                                    <MdArrowForwardIos />
                                </button>
                            </div>
                        )
                    }
                </div>
            </div>
    );
};
