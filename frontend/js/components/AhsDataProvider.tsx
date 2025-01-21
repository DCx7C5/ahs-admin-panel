import React, {createContext, useRef, ReactNode} from "react";


interface DataContextType {
  user: Record<string, any>;
  menuItems: Record<string, any>;
  socketUrl: string; // Notice this expects an object, not a string
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
  children: ReactNode;
}

export const AhsDataProvider: React.FC<DataProviderProps> = ({children}) => {

  const userRef = useRef(parseDataFromElement('user-data'));
  const menuRef = useRef(parseDataFromElement('menu-data'));
  const socketRef = useRef(parseDataFromElement('socket-url'))

  return (
    <DataContext.Provider
      value={{
        user: userRef.current,
        menuItems: menuRef.current,
        socketUrl: atob(socketRef.current["path"])
      }}
    >
      {children}
    </DataContext.Provider>
  );
};


export default AhsDataProvider;