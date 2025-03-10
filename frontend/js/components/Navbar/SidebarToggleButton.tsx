import React from "react";

interface Props {
    onToggle: () => void;
}

export const SidebarToggleButton: React.FC = ({ onToggle }: Props) => (
    <button onClick={onToggle} className="btn toggle-sidebar-btn">
        <i className="bi bi-list"></i>
    </button>
);

export default SidebarToggleButton;