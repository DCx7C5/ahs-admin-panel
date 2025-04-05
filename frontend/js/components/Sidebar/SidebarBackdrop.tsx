import React from 'react';


interface SidebarBackdropProps {
  onToggle: () => void;
}


export const SidebarBackdrop = ({onToggle}: SidebarBackdropProps) => {
  return <>
    <div className={`backdrop`}
         onClick={onToggle} // Close sidebar when backdrop is clicked
    />
  </>
}

export default SidebarBackdrop;