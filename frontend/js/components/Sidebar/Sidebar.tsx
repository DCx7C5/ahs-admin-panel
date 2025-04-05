import React, {RefObject, use, useRef} from 'react';
import SidebarFooter from "./SidebarFooter";
import SidebarProfile from "./SidebarProfile";
import SidebarMenu from "./SidebarMenu";
import useHideElement from "../../hooks/useHideElement";
import SidebarHeader from "./SidebarHeader";
import SidebarBackdrop from "./SidebarBackdrop";
import './sidebar.scss';
import {DataContext} from "../DataProvider";


export const Sidebar = () => {
  const sidebarRef = useRef(null);
  const { username, image } = use(DataContext);
  const [isVisible, hide,, toggleVisibility] = useHideElement(
    false,'sb.show', sidebarRef
  )

  return (
    <>
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