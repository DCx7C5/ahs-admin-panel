import React, {use, useEffect} from 'react';
import {DataContext} from "../DataProvider";
import SidebarMenuItem from "./SidebarMenuItem";


interface SidebarMenuProps {
  children?: React.ReactNode;
  onLinkClick?: (page: any) => void;
}

export const SidebarMenu = ({children, onLinkClick}: SidebarMenuProps) => {
  const {pages} = use(DataContext);

  useEffect(() => {
    console.log("SidebarMenu | Pages | ", pages);
  }, []);

  return <ul className="menu">
    {Array.isArray(pages) && pages.map((page, index) => (
      page.active && <SidebarMenuItem item={page} onLinkClick={onLinkClick} />
    ))}
    {children}
  </ul>
}


export default SidebarMenu;