import React from "react";
import {useLocation} from "react-router-dom";

export const SidebarMenuItem = ({item, onLinkClick}) => {
  const location = useLocation();
  const currentPath = location.pathname;

  const handleClick = (event, path) => {
    event.preventDefault();
    onLinkClick();
    window.location.href = path;
  };

  const renderMenuItem = (item, isSubmenu = false) => {
    const {order, path, name, icon, children} = item;
    const itemIsActive = currentPath === path;

    return (
      <li key={order} className={`${isSubmenu ? 'submenuitem' : 'menuitem'} ${children ? 'has-submenu' : ''}`}>
        <a
          className={`${isSubmenu ? 'submenulink' : 'menulink'} ${itemIsActive ? "active" : ""}`}
          onClick={(event) => handleClick(event, path)}
          href={path}
        >
          <span className={`${isSubmenu ? 'submenuicon' : 'menuicon'}`}>
            <i className={icon}></i>
          </span>
          <span className={`${isSubmenu ? 'submenulabel' : 'menulabel'}`}>{name}</span>
        </a>
        {children && (
          <ul className="submenu">
            {children.map((childItem) => renderMenuItem(childItem, true))}
          </ul>
        )}
      </li>
    );
  };

  return renderMenuItem(item); // Hier die Hauptitem-Ebene rendern
};

export default SidebarMenuItem;