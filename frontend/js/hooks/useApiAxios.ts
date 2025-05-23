import axios, { AxiosRequestConfig } from "axios";
import { useCallback, useState } from "react";

type JsonString = string;
type rdKey = string;
type rdValue = string | object | {} | ArrayBuffer | number[] | string[] | string[][];
type requestData = Record<rdKey, rdValue>;


export interface apiClient {
  get: (
      endpoint: string,
      data?: requestData,
  ) => Promise<any>;

  post: (
    endpoint: string,
    data?: requestData | JsonString,
  ) => Promise<any>;
  isLoading: boolean;
  error: string | null;
  setRequestInterceptor: (token: string) => void;
}

const api = axios.create({
    baseURL: `${window.location.origin}/`,
    httpsAgent: true,
    maxContentLength: 5000,
});


export const useApiAxios = (): apiClient => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const get = useCallback(
        async (endpoint: string, data: requestData) => {
            setIsLoading(true);

            const response = await api.request({
                url: endpoint,
                method: "GET",
            } as AxiosRequestConfig);

            setIsLoading(false);
            return response.data;
    },[setIsLoading]);

    const post = useCallback(async (
        endpoint: string,
        data: requestData | JsonString,
    ) => {
        setIsLoading(true);
        const cfg: AxiosRequestConfig = {
            url: endpoint,
            method: "POST",
            data: data,
        }

        if (typeof data === "string") {
            if (cfg.headers) {
                cfg.headers["Content-Type"] = "application/json"
            } else if (!cfg.headers) {
                cfg.headers = {}
                cfg.headers["Content-Type"] = "application/json"
            }
        }

        try {
            const response = await api.request(cfg);
            setIsLoading(false);
            return response.data;
        } catch (err) {
            console.error(err);
            setIsLoading(false);
            setError(err.message);
            return null;
        }
    }, [setIsLoading, setError]);

    const setRequestInterceptor = useCallback((token: string) => {
        api.interceptors.request.use(
            (config) => {
                config.headers = config.headers || {};
                config.headers["X-AHS-Token"] = `${token}`;
                return config;
            },
            (error) => Promise.reject(error),
        );
    }, []);

    return {
        get,
        post,
        isLoading,
        error,
        setRequestInterceptor,
    }
};

export default useApiAxios;