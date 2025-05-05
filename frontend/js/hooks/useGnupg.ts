import { useState, useCallback } from 'react';
import axios from 'axios';

// Define the types for our GnuPG operations
interface GnupgKey {
  fingerprint: string;
  name: string;
  email: string;
  created: string;
  expires?: string;
  type: 'public' | 'private';
}

interface KeyGenerationParams {
  name: string;
  email: string;
  comment?: string;
  passphrase: string;
  keyType?: string;
  keyLength?: number;
  expiry?: string;
}

interface EncryptParams {
  data: string;
  recipients: string[]; // Fingerprints or emails
  armor?: boolean;
}

interface DecryptParams {
  data: string;
  passphrase?: string;
}

interface SignParams {
  data: string;
  fingerprint: string;
  passphrase?: string;
  detached?: boolean;
}

interface VerifyParams {
  data: string;
  signature?: string; // For detached signatures
}

interface GnupgResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

interface gnupgApi {
  // Key management
  listKeys: () => Promise<GnupgResponse<GnupgKey[]>>;
  generateKey: (params: KeyGenerationParams) => Promise<GnupgResponse<GnupgKey>>;
  exportPublicKey: (fingerprint: string) => Promise<GnupgResponse<string>>;
  exportPrivateKey: (fingerprint: string) => Promise<GnupgResponse<string>>;
  importKey: (keyData: string) => Promise<GnupgResponse<GnupgKey[]>>;
  deleteKey: (fingerprint: string, type: 'public' | 'private') => Promise<GnupgResponse>;

  // Cryptographic operations
  encrypt: (params: EncryptParams) => Promise<GnupgResponse<string>>;
  decrypt: (params: DecryptParams) => Promise<GnupgResponse<string>>;
  sign: (params: SignParams) => Promise<GnupgResponse<string>>;
  verify: (params: VerifyParams) => Promise<GnupgResponse<{ valid: boolean; signatures: any[] }>>;

  // State
  loading: boolean;
  error: string | null;
}

export const useGnupg = (): gnupgApi => {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const apiCall = useCallback(async <T>(
    endpoint: string,
    method: 'GET' | 'POST' | 'DELETE' = 'GET',
    data?: any
  ): Promise<GnupgResponse<T>> => {
    setLoading(true);
    setError(null);

    try {
      const rData = {
        url: `/api/gpg/${endpoint}`,
        method,
        data,
        headers: {
          'Content-Type': 'application/json',
        },
      }
      const response = await axios(rData);

      return { success: true, data: response.data };
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      return { success: false, error: errorMessage };
    } finally {
      setLoading(false);
    }
  }, []);

  // Key management functions
  const listKeys = useCallback(async (): Promise<GnupgResponse<GnupgKey[]>> => {
    return apiCall<GnupgKey[]>('keys');
  }, [apiCall]);

  const generateKey = useCallback(async (
    params: KeyGenerationParams
  ): Promise<GnupgResponse<GnupgKey>> => {
    return apiCall<GnupgKey>('keys/generate', 'POST', params);
  }, [apiCall]);

  const exportPublicKey = useCallback(async (
    fingerprint: string
  ): Promise<GnupgResponse<string>> => {
    return apiCall<string>(`keys/${fingerprint}/export/public`);
  }, [apiCall]);

  const exportPrivateKey = useCallback(async (
    fingerprint: string
  ): Promise<GnupgResponse<string>> => {
    // Note: Backend should handle necessary security precautions
    return apiCall<string>(`keys/${fingerprint}/export/private`);
  }, [apiCall]);

  const importKey = useCallback(async (
    keyData: string
  ): Promise<GnupgResponse<GnupgKey[]>> => {
    return apiCall<GnupgKey[]>('keys/import', 'POST', { keyData });
  }, [apiCall]);

  const deleteKey = useCallback(async (
    fingerprint: string,
    type: 'public' | 'private'
  ): Promise<GnupgResponse> => {
    return apiCall(`keys/${fingerprint}?type=${type}`, 'DELETE');
  }, [apiCall]);

  // Cryptographic operations
  const encrypt = useCallback(async (
    params: EncryptParams
  ): Promise<GnupgResponse<string>> => {
    return apiCall<string>('encrypt', 'POST', params);
  }, [apiCall]);

  const decrypt = useCallback(async (
    params: DecryptParams
  ): Promise<GnupgResponse<string>> => {
    return apiCall<string>('decrypt', 'POST', params);
  }, [apiCall]);

  const sign = useCallback(async (
    params: SignParams
  ): Promise<GnupgResponse<string>> => {
    return apiCall<string>('sign', 'POST', params);
  }, [apiCall]);

  const verify = useCallback(async (
    params: VerifyParams
  ): Promise<GnupgResponse<{ valid: boolean; signatures: any[] }>> => {
    return apiCall<{ valid: boolean; signatures: any[] }>('verify', 'POST', params);
  }, [apiCall]);

  return {
    // Key management
    listKeys,
    generateKey,
    exportPublicKey,
    exportPrivateKey,
    importKey,
    deleteKey,

    // Cryptographic operations
    encrypt,
    decrypt,
    sign,
    verify,

    // State
    loading,
    error,
  };
};

export default useGnupg;