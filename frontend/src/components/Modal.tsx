import React from 'react';
import ClickAwayListener from 'react-click-away-listener';
import { ModalInterface } from '../types/modal';

export const Modal: React.FC<ModalInterface> = ({
    isOpen,
    title,
    message,
    primaryButton,
    secondaryButton,
}) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-start justify-center">
            {/* Overlay */}
            <div className="absolute inset-0 bg-black opacity-50"></div>
            
            {/* Modal */}
            <ClickAwayListener onClickAway={secondaryButton.onClick}>
                <div className="relative bg-black-light rounded-lg p-6 max-w-md w-full mx-4 shadow-xl border border-black-lighter top-[25%]">
                    {/* Title */}
                    <h2 className="text-xl font-semibold mb-4 text-white">
                        {title}
                    </h2>

                    {/* Message */}
                    <p className="text-gray-300 mb-6">
                        {message}
                    </p>

                    {/* Buttons */}
                    <div className="flex justify-end gap-3">
                        <button
                            onClick={secondaryButton.onClick}
                            className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white bg-black-lighter rounded-md transition-colors"
                        >
                            {secondaryButton.label}
                        </button>
                        <button
                            onClick={primaryButton.onClick}
                            disabled={primaryButton.isLoading}
                            className={`px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2`}
                        >
                            {primaryButton.isLoading && (
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            )}
                            {primaryButton.label}
                        </button>
                    </div>
                </div>
            </ClickAwayListener>
        </div>
    );
};