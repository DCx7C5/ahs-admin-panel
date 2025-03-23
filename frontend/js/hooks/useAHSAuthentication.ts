import {useRef, useState, useCallback, useEffect} from "react";
import {jwtDecode} from "jwt-decode";
import {apiClient} from "./useAHSApi";



export const useAHSAuthentication = (apiCli: apiClient) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);

  const urlRef = useRef({
    loginUrl: "api/token/",
    refreshUrl: "api/token/refresh/",
    blacklistUrl: "api/token/blacklist/",
  }).current;

  const { loginUrl, refreshUrl, blacklistUrl } = urlRef;

  useEffect(() => {
    console.log("useTokenAuth - Hook mounted");
    const accessToken = localStorage.getItem("access");
    const accExpired = checkTokenExpiration(accessToken);
    console.log(accessToken, accExpired);
    if (accessToken && !accExpired) {
      setAccessToken(accessToken);
      setIsAuthenticated(true);
    } else if (accessToken && accExpired) {
      const refreshToken = localStorage.getItem("refresh");
      const refExpired = checkTokenExpiration(refreshToken);
      if (refreshToken && !refExpired) {
        refreshAccessToken().then(r => console.log(r))
      }
    }
  }, [])

  const checkTokenExpiration = (token: string | null) => {
    if (!token) return true;
    const { exp } = jwtDecode(token);
    console.log(jwtDecode(token));
    return Date.now() >= exp * 1000;
  };

  // Login function
  const login = useCallback(async (username: string, password: string) => {
    try {
      const data = await apiCli.post(loginUrl, { username, password });
      console.log("DAAAAAAAATAAAA", data);
      setAccessToken(data.access);
      setIsAuthenticated(true);
      localStorage.setItem("refresh", data.refresh);
      localStorage.setItem("access", data.access);
      return data
    } catch (error) {
      console.error("Login failed:", error);
      setIsAuthenticated(true);
    }
  }, [apiCli, loginUrl]);

  const refreshAccessToken = useCallback(async () => {
    try {
      const refreshToken = localStorage.getItem("refresh");
      if (!refreshToken) {
          throw new Error("No refresh token found")
      }
      const data = await apiCli.post(refreshUrl, { refresh: refreshToken });
      localStorage.setItem("refresh", data.refresh);
      localStorage.setItem("access", data.access);

    } catch (error) {
      console.error("Token refresh failed:", error);
      await logout();
    }
  }, [apiCli, refreshUrl]);

  // Logout function (blacklist the token and clear data)
  const logout = useCallback(async () => {
    try {
      const refreshToken = localStorage.getItem("refresh");
      if (refreshToken) {
        await apiCli.get(blacklistUrl, { refresh: refreshToken });
      }
    } catch (error) {
      console.error("Token blacklist failed:", error);
    } finally {
      setAccessToken(null);
      setIsAuthenticated(false);
      localStorage.removeItem("refresh");
      localStorage.removeItem("access");
    }
  }, [apiCli, blacklistUrl]);

  return {
    isAuthenticated,
    accessToken,
    login,
    refreshAccessToken,
    logout,
  };
};

export default useAHSAuthentication;