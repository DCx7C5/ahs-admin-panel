import { useCallback, useEffect, useRef } from "react";

/**
 * A custom hook for managing timeouts in React components
 * @param callback - Function to call after the timeout expires
 * @param delay - Delay in milliseconds
 * @returns A tuple containing reset and clear functions
 */
export const useTimeout = (
  callback: () => void,
  delay: number
): [() => void, () => void] => {
  // Use MutableRefObject to avoid "possibly null" warnings
  const cbRef = useRef<() => void>(callback);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Update the callback ref when callback changes
  useEffect(() => {
    cbRef.current = callback;
  }, [callback]);

  // Set the timeout
  const set = useCallback(() => {
    timeoutRef.current = setTimeout(() => cbRef.current(), delay);
  }, [delay]);

  // Clear the timeout
  const clear = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  }, []);

  // Set timeout on mount and clear on unmount
  useEffect(() => {
    set();
    return clear;
  }, [delay, set, clear]);

  // Reset the timeout (clear and set again)
  const reset = useCallback(() => {
    clear();
    set();
  }, [clear, set]);

  return [reset, clear];
};

export default useTimeout;
