import React, {use, useRef} from 'react';
import {createPortal} from "react-dom";
import {DataContext} from "../DataProvider";
import SidebarFooter from "./SidebarFooter";
import SidebarProfile from "./SidebarProfile";
import SidebarMenu from "./SidebarMenu";
import SidebarToggleButton from "./SidebarToggleButton";
import useHideElement from "../../hooks/useHideElement";
import SidebarHeader from "./SidebarHeader";
import SidebarBackdrop from "./SidebarBackdrop";
import './sidebar.scss';


export const Sidebar = ({toggleClass}) => {
  const sidebarRef = useRef(null);
  const { username, image } = use(DataContext).user;
  const [isVisible, hide,, toggleVisibility] = useHideElement(
    false,'sb.show', sidebarRef
  )

  return (
    <>
      {createPortal(
        <SidebarToggleButton onToggle={toggleVisibility} />,
        document.getElementById(toggleClass)
      )}
      {isVisible && <SidebarBackdrop onToggle={toggleVisibility} />}
      <div ref={sidebarRef} className='sidebar'>
        <SidebarHeader />
        <SidebarMenu onLinkClick={hide} />
        <SidebarFooter>
          <SidebarProfile imagePath={image} userName={username} />
        </SidebarFooter>
      </div>
    </>
  );
};

export default Sidebar;