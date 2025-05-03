import { useEffect, useState, RefObject } from "react";
import { useLocalStorage } from "./useStorage";

type UseHideElementReturn = [
  boolean,
  () => void,
  () => void,
  () => void
];

export const useHideElement = (
  initialValue: boolean = false, 
  storageKey: string | null = null, 
  elementRef: RefObject<HTMLElement> | null = null
): UseHideElementReturn => {
  const [isVisible, setIsVisible] = (typeof storageKey === 'string')
    ? useLocalStorage<boolean>(storageKey, initialValue)
    : useState<boolean>(initialValue);

  useEffect(() => {
    if (elementRef?.current && isVisible && !elementRef.current.classList.contains('visible'))
      show();
  }, []);

  const hide = (): void => {
    setIsVisible(false);
    if (elementRef?.current) elementRef.current.classList.remove('visible');
  };

  const show = (): void => {
    setIsVisible(true);
    if (elementRef?.current) elementRef.current.classList.add('visible');
  };

  const toggle = (): void => {
    setIsVisible((prev) => !prev);
    if (elementRef?.current) elementRef.current.classList.toggle('visible');
  };

  return [
    isVisible,
    hide,
    show,
    toggle
  ];
};

export default useHideElement;
