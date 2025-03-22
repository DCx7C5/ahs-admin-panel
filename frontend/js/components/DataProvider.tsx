import React, {createContext, ReactNode, useState} from "react";
import useAHSApi from "../hooks/useAHSApi";
import useCryptography from "../hooks/useCryptography";
import useAHSToken from "../hooks/useAHSToken";
import useIndexedDB from "../hooks/useIndexedDB";


export interface DataContextType {
    apiClient?: any,
    cryptoClient?: any,
    isAuthenticated: boolean;
    setIsAuthenticated: (value: (((prevState: boolean) => boolean) | boolean)) => void;
    isSuperUser: boolean;
    setIsSuperUser: (value: ((prevState: boolean) => boolean) | boolean) => void;
}

export const DataContext = createContext<DataContextType | null>(null);


interface DataProviderProps {
  children: ReactNode;
}


export const DataProvider: React.FC<DataProviderProps> = ({children}) => {
  const [isAuthenticated , setIsAuthenticated] = useState<boolean>(false);
  const [isSuperUser, setIsSuperUser] = useState<boolean>(false);
  //const apiClient = useAHSApi();
  const indexedDbClient = useIndexedDB();
  const cryptoClient = useCryptography(indexedDbClient);
  //const token = useAHSToken(cryptoClient)


  return (
    <DataContext.Provider
      value={{
        cryptoClient,
        isAuthenticated,
        setIsAuthenticated,
        isSuperUser,
        setIsSuperUser,
      }}
    >
      {children}
    </DataContext.Provider>
  );
};


export default DataProvider;