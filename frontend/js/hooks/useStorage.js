import { useCallback, useEffect, useState } from "react";
import PropTypes from 'prop-types';

export const useStorage = (key, defaultValue, storage) => {
  const [value, setValue] = useState(() => {
    const item = storage.getItem(key);
    if (item !== null) return JSON.parse(item);
    return defaultValue;
  });

  useEffect(() => {
    if (value === undefined) return storage.removeItem(key);
    storage.setItem(key, JSON.stringify(value));
  }, [key, value, storage]);

  const remove = useCallback(() => {
    setValue(undefined);
  }, []);

  return [value, setValue, remove];
};

useStorage.propTypes = {
  key: PropTypes.string,
  defaultValue: PropTypes.any,
  storage: PropTypes.shape({
    getItem: PropTypes.func.isRequired,
    setItem: PropTypes.func.isRequired,
    removeItem: PropTypes.func.isRequired,
  }).isRequired,
};

export const useLocalStorage = (key, defaultValue) => {
  return useStorage(key, defaultValue, window.localStorage);
};

export const useSessionStorage = (key, defaultValue) => {
  return useStorage(key, defaultValue, window.sessionStorage);
};

export default {useStorage, useLocalStorage, useSessionStorage};
