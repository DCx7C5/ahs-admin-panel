import { useState, useCallback } from 'react';


const getCsrfToken = async (): Promise<string | null> => {
  const metaToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
  if (metaToken) return metaToken;

  // Fallback: Fetch CSRF token from Django endpoint (if configured)
  try {
    const response = await fetch('/api/get-csrf-token/', { credentials: 'include' });
    const data = await response.json();
    return data.csrfToken || null;
  } catch {
    return null;
  }
};

// Default headers
const defaultHeaders: Record<string, string> = {
  'Content-Type': 'application/json',
};

// API response type
interface ApiResponse<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

// Options for the fetch request
interface FetchOptions extends Omit<RequestInit, 'body'> {
  headers?: Record<string, string>;
  body?: string | Record<string, unknown>;
}


const useApiFetch = () => {
  const [response, setResponse] = useState<ApiResponse<unknown>>({
    data: null,
    loading: false,
    error: null,
  });

  const request = useCallback(async <T>(
    url: string,
    method: string,
    options: FetchOptions = {}
  ): Promise<ApiResponse<T>> => {
    setResponse({ data: null, loading: true, error: null });

    try {
      const headers = new Headers({ ...defaultHeaders, ...options.headers });

      // Add CSRF token for non-GET requests (Two Scoops, Section 13.3)
      if (method.toUpperCase() !== 'GET') {
        const csrfToken = await getCsrfToken();
        if (csrfToken) {
          headers.set('X-CSRFToken', csrfToken);
        }
      }

      // Add authentication token (if applicable)
      const authToken = localStorage.getItem('authToken');
      if (authToken) {
        headers.set('Authorization', `Bearer ${authToken}`);
      }

      // Handle body: string or object
      let body: string | undefined;
      if (options.body) {
        if (typeof options.body === 'string') {
          body = options.body;
        } else {
          body = JSON.stringify(options.body);
        }
      }

      const fetchOptions: RequestInit = {
        ...options,
        method,
        headers,
        body,
      };

      const res = await fetch(`/api${url}`, fetchOptions);

      // Check for HTTP errors (Two Scoops, Section 17.3.7: Test Your API)
      if (!res.ok) {
        if (res.status === 401) {
          window.location.href = '/login'; // Handle unauthorized (Two Scoops, Section 8.4.2)
        }
        throw new Error(`HTTP error! Status: ${res.status}`);
      }

      const data: T = await res.json();
      setResponse({ data, loading: false, error: null });
      return { data, loading: false, error: null };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error';
      setResponse({ data: null, loading: false, error: errorMessage });
      return { data: null, loading: false, error: errorMessage };
    }
  }, []);

  const get = useCallback(
    <T>(url: string, options: Omit<FetchOptions, 'method' | 'body'> = {}) =>
      request<T>(url, 'GET', options),
    [request]
  );

  const post = useCallback(
    <T>(url: string, options: FetchOptions = {}) => request<T>(url, 'POST', options),
    [request]
  );

  return {
    request,
    get,
    post,
    data: response.data,
    loading: response.loading,
    error: response.error,
  };
};

export default useApiFetch;