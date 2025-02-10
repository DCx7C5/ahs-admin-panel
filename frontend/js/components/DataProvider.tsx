import React, {createContext, useRef, ReactNode, useEffect} from "react";


export interface DataContextType {
  user: Record<string, any>;
  pages: any;
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

export const DataProvider: React.FC<DataProviderProps> = ({children}) => {

  const userRef = useRef(parseDataFromElement('user-data'));
  const pagesRef = useRef(parseDataFromElement('page-data'));

  return (
    <DataContext.Provider
      value={{
        user: userRef.current,
        pages: pagesRef.current,
      }}
    >
      {children}
    </DataContext.Provider>
  );
};


export default DataProvider;