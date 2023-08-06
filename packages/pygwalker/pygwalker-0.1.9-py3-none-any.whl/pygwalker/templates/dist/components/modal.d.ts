import React from "react";
interface ModalProps {
    onClose?: () => void;
    show?: boolean;
    title?: string;
}
declare const Modal: React.FC<ModalProps>;
export default Modal;
