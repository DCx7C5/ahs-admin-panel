import React, {createContext, ReactNode, useCallback, useEffect, useRef, useState} from "react";
import useAHSApi, {apiClient} from "../hooks/useAHSApi";


export interface DataContextType {
    apiCli: apiClient;
    isAuthenticated: boolean;
    setIsAuthenticated: (value: boolean) => void;
    isSuperUser: boolean;
    setIsSuperUser: (value: boolean) => void;
    user: User | {};
    setUserProperty: (key: string, value: string | boolean | number) => void;
}


export const DataContext = createContext<DataContextType | null>(null);


interface DataProviderProps {
  children: ReactNode;
}


interface User {
    userName: string;
}


export const DataProvider: React.FC<DataProviderProps> = ({children}) => {
    const apiCli = useAHSApi();
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isSuperUser, setIsSuperUser] = useState(false);
    const user = useRef<User | {}>({}).current;

    useEffect(() => {

        return () => {
            if (apiCli) console.log("DataProvider | Unmounting, disconnecting socket")
            setIsAuthenticated(false)
            setIsSuperUser(false)
        }
    }, []);

    const setUserProperty = useCallback( (key: string, value: string | boolean | number) => {
    },[user])

    return (
        <DataContext.Provider
            value={{
            apiCli,
            isAuthenticated,
            setIsAuthenticated,
            isSuperUser,
            setIsSuperUser,
            user,
            setUserProperty,
        }}
        >
        {children}
        </DataContext.Provider>
    );
};


export default DataProvider;