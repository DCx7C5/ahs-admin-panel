import React from "react";

interface SidebarHeaderProps {
  children: React.ReactNode;
}

export const SidebarHeader = ({children}: SidebarHeaderProps) => {

  return <div className="sidebar-header">
    {children}
  </div>
}

export default SidebarHeader;