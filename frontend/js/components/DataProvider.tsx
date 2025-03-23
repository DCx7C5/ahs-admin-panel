import React, {createContext, ReactNode, useEffect, useState} from "react";
import useCryptography from "../hooks/useCryptography";
import useAHSToken from "../hooks/useAHSToken";
import useAHSApi from "../hooks/useAHSApi";
import useAHSAuthentication from "../hooks/useAHSAuthentication";


export interface DataContextType {
    apiCli?: any,
    cryptoCli?: any,
    isAuthenticated: boolean;
    isSuperUser: boolean;
    setIsSuperUser: (value: ((prevState: boolean) => boolean) | boolean) => void;
}

export const DataContext = createContext<DataContextType | null>(null);


interface DataProviderProps {
  children: ReactNode;
}


export const DataProvider: React.FC<DataProviderProps> = ({children}) => {
  const [isSuperUser, setIsSuperUser] = useState<boolean>(false);
  const apiCli = useAHSApi();
  const {isAuthenticated} = useAHSAuthentication(apiCli)
  const cryptoCli = useCryptography();
  //const {token, addTokenPayload} = useAHSToken(cryptoCli);

  useEffect(() => {
    console.log("DataProvider | Init | Mounting component")

    return () => {
        console.log("DataProvider | Unmounting, disconnecting socket")
    }
  }, []);

  return (
    <DataContext.Provider
      value={{
        apiCli,
        cryptoCli,
        isAuthenticated,
        isSuperUser,
        setIsSuperUser,
      }}
    >
      {children}
    </DataContext.Provider>
  );
};


export default DataProvider;