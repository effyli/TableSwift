import React, { createContext, useContext, useState } from 'react';
import { ModalInterface } from '../types/modal';
import { Modal } from '../components/Modal';

interface ModalContextType {
    modal: ModalInterface | null;
    handleModal: (modal: ModalInterface) => void;
    hideModal: () => void;
}

const initialState: ModalContextType = {
    modal: null,
    handleModal: () => {},
    hideModal: () => {},
};

export const ModalContext = createContext<ModalContextType>(initialState);

export const ModalProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [modal, setModal] = useState<ModalInterface | null>(null);

    const handleModal = (modalConfig: ModalInterface) => {
        console.log('Modal:', modalConfig);
        setModal(modalConfig);
    };

    const hideModal = () => {
        setModal(null);
    };

    return (
        <ModalContext.Provider value={{ modal, handleModal, hideModal }}>
            <Modal
                isOpen={modal !== null && modal?.isOpen}
                title={modal?.title || ''}
                message={modal?.message || ''}
                primaryButton={{
                    label: modal?.primaryButton.label || '',
                    onClick: modal?.primaryButton.onClick || (() => {}),
                    isLoading: modal?.primaryButton.isLoading || false,
                }}
                secondaryButton={{
                    label: modal?.secondaryButton.label || '',
                    onClick: modal?.secondaryButton.onClick || (() => {}),
                }}
            />
            {children}
        </ModalContext.Provider>
    );
};

export const useModal = () => useContext(ModalContext);