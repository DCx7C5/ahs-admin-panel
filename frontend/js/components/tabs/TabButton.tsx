import React, {startTransition} from "react";


interface TabButtonProps {
    action: () => void;
    isActive: boolean;
    children: React.ReactNode;
}


export const TabButton: React.FC<TabButtonProps> = ({action, isActive, children}) => {
  if (isActive) {
    return <b>{children}</b>
  }

  const handleClick = () => {
      startTransition(() => {
            action();
      });
  }

  return (
    <button onClick={handleClick}
            className="tab-button"
    >
      {children}
    </button>
  );
}


export default TabButton;