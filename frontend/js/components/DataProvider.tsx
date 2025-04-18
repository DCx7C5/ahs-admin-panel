import React, {createContext, ReactNode, useEffect, useState} from "react";
import useECCryptography, {cryptoApi} from "../hooks/useECCryptography";
import useAHSToken from "../hooks/useAHSToken";
import useAHSApi, {apiClient} from "../hooks/useAHSApi";


export interface DataContextType {
    apiCli: apiClient;
    cryptoCli: cryptoApi;
    isAuthenticated: boolean;
    isSuperUser: boolean;
    user: User | null;
}


export const DataContext = createContext<DataContextType | null>(null);


interface DataProviderProps {
  children: ReactNode;
}

interface AHSData {
    options?: any;
    uid?: string;
    challenge?: string;
}

interface User {
    userName: string;
}

interface Window {
    __AHS_DATA__?: AHSData;
}


export const DataProvider: React.FC<DataProviderProps> = ({children}) => {
    const apiCli = useAHSApi();
    //const gpgApi = useGnupg();
    const cryptoCli = useECCryptography();
    const {token, get} = useAHSToken(cryptoCli);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isSuperUser, setIsSuperUser] = useState(false);
    const [user, setUser] = useState<User | null>(null);

    useEffect(() => {
        //console.log(gpgApi.listKeys())
        if (!token) {
            console.log("DataProvider | No token")
            return
        }
        apiCli.setRequestInterceptor(token)
        return () => {
            if (apiCli && cryptoCli) console.log("DataProvider | Unmounting, disconnecting socket")
            setIsAuthenticated(false)
            setIsSuperUser(false)
            setUser(null)
        }
    }, []);

  return (
    <DataContext.Provider
      value={{
        apiCli,
        cryptoCli,
        isAuthenticated,
        isSuperUser,
        user,
      }}
    >
      {children}
    </DataContext.Provider>
  );
};


export default DataProvider;