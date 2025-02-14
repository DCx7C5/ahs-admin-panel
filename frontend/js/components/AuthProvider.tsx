import React, {createContext, useState, useEffect, use, useRef} from "react";
import api from "../axios";



interface AuthContextProps {
  isAuthenticated: boolean;
  handleLogin: (credentials) => void;
  handleLogout: () => void;
}
export const AuthContext = createContext<AuthContextProps | undefined>(undefined);


export const AuthProvider = ({ children }) => {
  const { loginUrl, logoutUrl } = useRef({
      "loginUrl": "/login/",
      "logoutUrl": "/logout/",
      "refresh": "/refresh/",
  });
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check for stored tokens on mount
    const token = localStorage.getItem("access_token");
    setIsAuthenticated(!!token);
  }, []);

  const handleLogin = async (credentials) => {
      const response = await api.post("/token/", credentials);
      const { access, refresh } = response.data;

      localStorage.setItem("access", access);
      localStorage.setItem("refresh", refresh);

      return response.data;
  };

  const handleLogout = () => {
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
      setIsAuthenticated(false);

  };

  return (
    <AuthContext.Provider
      value={{
          isAuthenticated,
          handleLogin,
          handleLogout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export default AuthProvider;