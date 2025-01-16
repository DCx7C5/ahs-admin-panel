import React, { createContext, useRef, ReactNode} from "react";


interface DataContextType {
  user: Record<string, any>;
  menuItems: Record<string, any>;
}

export const DataContext = createContext<DataContextType | null>(null);

const parseDataFromElement = (dataElementId: string): Record<string, any> => {
  const elem = document.getElementById(dataElementId);
  try {
    return elem ? JSON.parse(elem.textContent || "") || {} : {};
  } catch (e) {
    console.error(`Error parsing JSON data for element ${dataElementId}: ${(e as Error).message}`);
    return {};
  }
};


interface DataProviderProps {
  userElementId: string;
  menuElementId: string;
  children: ReactNode;
}

export const DataProvider: React.FC<DataProviderProps> = ({
  userElementId,
  menuElementId,
  children,
}) => {

  const userRef = useRef({ user: parseDataFromElement(userElementId) });
  const menuRef = useRef({ menuItems: parseDataFromElement(menuElementId) });

  return (
    <DataContext.Provider
      value={{
        user: userRef.current.user,
        menuItems: menuRef.current.menuItems,
      }}
    >
      {children}
    </DataContext.Provider>
  );
};


export default DataProvider;