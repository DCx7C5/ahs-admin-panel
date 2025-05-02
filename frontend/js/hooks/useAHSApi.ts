import axios, {AxiosRequestConfig, AxiosResponse} from "axios";
import React, {useCallback, useEffect, useState} from "react";


export interface apiClient {
  get: (endpoint: string, requestData?: any, config?: any) => Promise<any>;
  post: (endpoint: string, requestData?: any, config?: any) => Promise<any>;
  isLoading: boolean;
  error: string;
  data: any;
  setRequestInterceptor: (token: string) => void;
}

const api = axios.create({
  baseURL: `${window.location.origin}/`,
  httpsAgent: false,
});

api.defaults.headers.post['Content-Type'] = 'application/json';
api.defaults.headers.get['Content-Type'] = 'application/json';


export const useAHSApi = (): apiClient => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState({});

  useEffect(() => {
    console.log("useAHSApi initialized")

    return () => {
      console.log("useAHSApi cleanup")
    }
  }, []);

  const request = useCallback(
    async (endpoint, method="POST", requestData={}, config={}): Promise<AxiosResponse> => {
      setIsLoading(true);
      setError(null);

      try {
        const requestConfig: AxiosRequestConfig = {
          url: endpoint, // Endpoint to hit
          method, // HTTP method (e.g., GET, POST)
          data: requestData, // Data to send in the request body
          ...config, // Additional Axios configurations, if provided
        };
        const response = await api.request(requestConfig);

        setData((prev) => ({ ...prev, [endpoint]: response.data }));
        return response;
      } catch (err) {
        setError(err.response?.data?.message || err.message || "Something went wrong");
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const get = useCallback(
    async (endpoint: string, requestData: any = {}, config: any = {}): Promise<AxiosResponse> => {
      const response = await request(endpoint, 'GET', requestData, config);
      return response.data;
    }, [request]
  );

  const post = useCallback(
    async (endpoint: string, requestData: any = {}, config: any = {}): Promise<AxiosResponse> => {
      const response = await request(endpoint, 'POST', requestData, config);
        return response.data;
    }, [request]
  );

  const setRequestInterceptor = useCallback((token: string) => {
    api.interceptors.request.use(
      (config) => {
        config.headers['X-AHS-Token'] = `${token}`;
        console.log('RequestInterceptor ', config.headers['X-AHS-Token'], '')
        return config;
      },
      (error) => {
        console.error('RequestInterceptor failed',error);
        return Promise.reject(error);
      }
    );
  },[])

  return {
    get,
    post,
    isLoading,
    error,
    data,
    setRequestInterceptor,
  };
};

export default useAHSApi;