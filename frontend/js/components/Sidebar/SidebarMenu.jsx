import React, {use, useEffect} from 'react';
import {DataContext} from "../DataProvider";
import SidebarMenuItem from "./SidebarMenuItem";




export const SidebarMenu = ({children, onLinkClick}) => {
  const {pages} = use(DataContext);

  useEffect(() => {
    console.log("SidebarMenu | Pages | ", pages);
  }, []);

  return <ul className="menu">
    {Array.isArray(pages) && pages.map((page, index) => (
      page.active && <SidebarMenuItem key={index} item={page} onLinkClick={onLinkClick} />
    ))}
    {children}
  </ul>
}


export default SidebarMenu;