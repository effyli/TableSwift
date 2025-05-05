export interface ModalInterface {
    isOpen: boolean;
    title: string;
    message: string;
    primaryButton: {
        label: string;
        onClick: () => void;
        isLoading?: boolean;
    };
    secondaryButton: {
        label: string;
        onClick: () => void;
    };
}