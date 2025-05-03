import axios, { AxiosRequestConfig } from "axios";
import { useCallback, useState } from "react";
import {base64UrlEncode} from "../components/utils";

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
    data?: requestData,
    json?: JsonString,
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


export const useAHSApi = (): apiClient => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    function encodeTypedArrays(obj: requestData) {
        const isTypedArray = (value: rdValue) => ArrayBuffer.isView(value);

        return Object.fromEntries(
            Object.entries(obj).map(([key, value]) =>
            isTypedArray(value)
                ? [key, base64UrlEncode(value.buffer)]
                : [key, value]
            )
        );
    }

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
        data: requestData,
        json: string,
        autoEncode: boolean = false,
    ) => {
        setIsLoading(true);
        const cfg: AxiosRequestConfig = {
            url: endpoint,
            method: "POST",
        }

        if (json) {
            cfg.data = json
            if (cfg.headers) {
                cfg.headers["Content-Type"] = "application/json"
            } else if (!cfg.headers) {
                cfg.headers = {}
                cfg.headers["Content-Type"] = "application/json"
            }
        } else if (data) {
            cfg.data = data
        }

        if (autoEncode) {
            encodeTypedArrays(cfg.data as requestData)
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

export default useAHSApi;