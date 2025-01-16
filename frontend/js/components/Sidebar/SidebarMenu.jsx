import React, {use} from 'react';
import {DataContext} from "../DataProvider";
import SidebarMenuItem from "./SidebarMenuItem";




export const SidebarMenu = ({children, onLinkClick}) => {
  const menuItems = use(DataContext).menuItems;
  const filteredItems = menuItems.filter(item => item.parent === 1 || item.parent === null);
  

  return <ul className="menu">
    {filteredItems.map((item, index) => (
      <SidebarMenuItem key={index} item={item} onLinkClick={onLinkClick} />
    ))}
    {children}
  </ul>
}


export default SidebarMenu;