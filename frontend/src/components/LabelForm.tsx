import React, { useState, useEffect } from 'react';
import { Labels } from '../types/labels';

interface LabelFormProps {
    labels: Labels;
    generateCode: () => void;
}

export const LabelForm: React.FC<LabelFormProps> = ({ labels, generateCode }) => {
    const [isLoadingGenerating, setIsLoadingGenerating] = useState(false);

    const handleGenerateCode = () => {
        setIsLoadingGenerating(true);
        try {
            generateCode();
        } catch (error) {
            console.error('Error generating labels:', error);
        } finally {
            setIsLoadingGenerating(false);
        }
    };

    return (
        <div className="mt-12 border-t border-gray-700 pt-12">
            <h3 className="text-lg font-semibold text-white">Generated Code</h3>
            {/* <pre className="bg-gray-800 text-gray-300 p-4 rounded">{JSON.stringify(labels[activeLabels], null, 2)}</pre> */}
            <button
                onClick={() => handleGenerateCode()}
                disabled={isLoadingGenerating}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg transition-colors disabled:opacity-50"
            >
                {isLoadingGenerating ? 'Generating...' : 'Generate Code'}
            </button>
        </div>
    );
};
