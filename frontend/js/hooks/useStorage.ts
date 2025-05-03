import { useCallback, useEffect, useState, Dispatch, SetStateAction } from "react";

// Define types for the storage interface
interface StorageInterface {
  getItem: (key: string) => string | null;
  setItem: (key: string, value: string) => void;
  removeItem: (key: string) => void;
}

// Return type for useStorage hook
type UseStorageReturnType<T> = [
  T,
  Dispatch<SetStateAction<T>>,
  () => void
];

/**
 * A custom hook for persisting state in web storage (localStorage or sessionStorage)
 * @template T - Type of the stored value
 * @param key - The storage key
 * @param defaultValue - The default value if no item exists in storage
 * @param storage - The storage object (localStorage or sessionStorage)
 * @returns A tuple containing the value, a setter function, and a remove function
 */
export const useStorage = <T>(
  key: string,
  defaultValue: T,
  storage: StorageInterface
): UseStorageReturnType<T> => {
  const [value, setValue] = useState<T>(() => {
    const item = storage.getItem(key);
    if (item !== null) return JSON.parse(item) as T;
    return defaultValue;
  });

  useEffect(() => {
    if (value === undefined) {
      storage.removeItem(key);
      return;
    }
    storage.setItem(key, JSON.stringify(value));
  }, [key, value, storage]);

  const remove = useCallback(() => {
    setValue(undefined as unknown as T);
  }, []);

  return [value, setValue, remove];
};

/**
 * A custom hook for persisting state in localStorage
 * @template T - Type of the stored value
 * @param key - The storage key
 * @param defaultValue - The default value if no item exists in storage
 * @returns A tuple containing the value, a setter function, and a remove function
 */
export const useLocalStorage = <T>(
  key: string,
  defaultValue: T
): UseStorageReturnType<T> => {
  return useStorage<T>(key, defaultValue, window.localStorage);
};

/**
 * A custom hook for persisting state in sessionStorage
 * @template T - Type of the stored value
 * @param key - The storage key
 * @param defaultValue - The default value if no item exists in storage
 * @returns A tuple containing the value, a setter function, and a remove function
 */
export const useSessionStorage = <T>(
  key: string,
  defaultValue: T
): UseStorageReturnType<T> => {
  return useStorage<T>(key, defaultValue, window.sessionStorage);
};

// Export individual hooks and a default object
const storageHooks = { useStorage, useLocalStorage, useSessionStorage };
export default storageHooks;
