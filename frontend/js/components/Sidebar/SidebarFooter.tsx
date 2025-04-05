import React from "react";

interface SidebarFooterProps {
  children: React.ReactNode;
}

export const SidebarFooter = ({children}: SidebarFooterProps) => {

  return <div className="sidebar-footer">
    {children}
  </div>
}

export default SidebarFooter;