import axios, {AxiosResponse} from "axios";
import {useCallback, useState} from "react";


export interface apiClient {
  get: (endpoint: string, requestData?: any, config?: any) => Promise<any>;
  post: (endpoint: string, requestData?: any, config?: any) => Promise<any>;
  isLoading: boolean;
  error: string;
  data: any;
}



export const useAHSApi = (): apiClient => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState({});

  const api = axios.create({
    baseURL: `${window.location.origin}/`,
    httpsAgent: false,

  });

  const request = useCallback(
    async (endpoint, method="POST", requestData={}, config={}): Promise<AxiosResponse> => {
      setIsLoading(true);
      setError(null);

      try {
        const cfg = {endpoint, method, requestData, ...config,}
        const response = await api.request(cfg);

        setData((prev) => ({ ...prev, [endpoint]: response.data }));
        return response.data;
      } catch (err) {
        setError(err?.response?.data?.message || err.message || "Something went wrong");
        throw err;
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const get = useCallback(
    async (endpoint: string, requestData: any = {}, config: any = {}): Promise<AxiosResponse> => {
      const response = await request(endpoint, 'GET', config);
      return response.data;
    }, [request]
  );

  const post = useCallback(
    async (endpoint: string, requestData: any = {}, config: any = {}): Promise<AxiosResponse> => {
      const response = await request(endpoint, 'POST', config);
      return response.data;
    }, [request]
  );

  return {
    get,
    post,
    isLoading,
    error,
    data,
  };
};

export default useAHSApi;