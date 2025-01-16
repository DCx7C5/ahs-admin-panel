import React from 'react';



export const SidebarBackdrop = ({onToggle}) => {
  return <>
    <div className={`backdrop`}
         onClick={onToggle} // Close sidebar when backdrop is clicked
    />
  </>
}

export default SidebarBackdrop;