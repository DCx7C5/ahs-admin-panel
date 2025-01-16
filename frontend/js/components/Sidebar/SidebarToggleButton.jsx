import React from "react";

export const SidebarToggleButton = ({ onToggle }) => (
    <button onClick={onToggle} className="btn toggle-sidebar-btn">
        <i className="bi bi-list"></i>
    </button>
);

export default SidebarToggleButton;