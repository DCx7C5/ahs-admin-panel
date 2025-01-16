import React, {useCallback, useEffect, useRef, useState} from "react";
import {useLocalStorage} from "./useStorage";

type UseDraggableArgs = {
  elementRef: React.RefObject<HTMLElement>;
  mode?: 'free' | 'snap';
  gridSize: number;
  parentElementRef?: React.RefObject<HTMLDivElement>;
  uniqueId?: string | number;
  dragElementRef?: React.RefObject<HTMLElement>;
};

export const useDraggable = ({
  elementRef,
  gridSize,
  parentElementRef = undefined,
  dragElementRef = undefined,
  uniqueId = undefined,
  mode = 'free'
}: UseDraggableArgs) => {
  const isDragging = useRef<boolean>(false);
  const mouseDown = useRef<boolean>(false);
  const frameId = useRef<number>(0);
  const startPosRefX = useRef(0);
  const startPosRefY = useRef(0);

  const  [storagePosition, setStoragePosition, _]  = useLocalStorage(
    `drag.pos.${uniqueId}`,
    { dx: 0, dy: 0 }
  );
  const [{ dx, dy }, setOffPosition] = useState<{ dx: number | null; dy: number | null }>({
    dx: null,
    dy: null,
  });

  useEffect(() => {
    if (elementRef && elementRef.current && storagePosition) {
      if (!storagePosition.dx || !storagePosition.dy) {
        setStoragePosition({dx: elementRef.current.offsetLeft, dy: elementRef.current.offsetTop});
      }
    }
  }, [elementRef]);

  const restrictWithinBounds = useCallback((value: number, min: number, max: number): number => {
    return Math.min(Math.max(value, min), max);
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent<HTMLElement>) => {
    if (elementRef.current.style.hasOwnProperty('transform')) console.log("transform yes");
    e.preventDefault();
    mouseDown.current = true;
    startPosRefX.current = e.clientX - dx
    startPosRefY.current = e.clientY - dy
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
  }, [dx, dy, elementRef]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    e.preventDefault();

    elementRef.current.style.zIndex = '15';
    isDragging.current = true;

    const ddx = e.clientX - startPosRefX.current;
    const ddy = e.clientY - startPosRefY.current;

    const parentBounds = parentElementRef?.current?.getBoundingClientRect();
    const snappedX = parentBounds
          ? restrictWithinBounds(
              Math.round(ddx / gridSize) * gridSize,
              0,
              parentBounds.width - (elementRef.current?.offsetWidth || 0)
            )
          : Math.round(ddx / gridSize) * gridSize;

    const snappedY = parentBounds
          ? restrictWithinBounds(
              Math.round(ddy / gridSize) * gridSize,
              0,
              parentBounds.height - (elementRef.current?.offsetHeight || 0)
            )
          : Math.round(ddy / gridSize) * gridSize;

    setOffPosition({dx: snappedX, dy: snappedY });
    frameId.current = requestAnimationFrame(() => {})

  },[gridSize, parentElementRef, restrictWithinBounds, elementRef]);

  const handleMouseUp = useCallback((e: MouseEvent) => {
    e.preventDefault();
    elementRef.current.style.removeProperty('z-index')
    mouseDown.current = false;
    isDragging.current = false;
    cancelAnimationFrame(frameId.current);
    frameId.current = 0;
    startPosRefX.current = 0;
    startPosRefY.current = 0;

    setStoragePosition({dx: dx, dy: dy});
    window.removeEventListener("mousemove", handleMouseMove);
    window.removeEventListener("mouseup", handleMouseUp);
  }, [dx, dy, setStoragePosition, handleMouseMove, elementRef]);

  return [dx, dy, handleMouseDown, isDragging];
};

export default useDraggable;