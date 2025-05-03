import { useEffect, useRef, useState, RefObject, MouseEvent as ReactMouseEvent } from "react";
import { useLocalStorage } from "./useStorage";

type Position = [number, number];
type PositionStorage = [number | null, number | null];
type UseMoveElementReturn = [Position, (e: ReactMouseEvent) => void];

const useMoveElement = (
  elementRef: RefObject<HTMLElement>,
  minX: number = 0,
  minY: number = 0
): UseMoveElementReturn => {
  const [position, setPosition] = useState<Position>([0, 0]);
  const isDownRef = useRef<boolean>(false);
  const isDraggingRef = useRef<boolean>(false);
  const deltaRef = useRef<Position>([0, 0]);
  const frameId = useRef<number>(0);
  const [positionStorage, setPositionStorage] = useLocalStorage<PositionStorage>(
    'posStorage', [null, null]);

  useEffect(() => {
    if (elementRef.current) {
      elementRef.current.style.position = "absolute";

      const parent = elementRef.current.parentElement;

      if (parent) {
        const maxX = parent.clientWidth - elementRef.current.clientWidth;
        const maxY = parent.clientHeight - elementRef.current.clientHeight;

        (positionStorage[0] !== null && positionStorage[1] !== null)
          ? setPosition([
              Math.min(positionStorage[0], maxX),
              Math.min(positionStorage[1], maxY),
            ])
          : setPosition([elementRef.current.offsetLeft, elementRef.current.offsetTop]);
      }
    }

    if (elementRef.current) {
      console.log(elementRef.current.offsetLeft, elementRef.current.offsetTop);
    }

    return () => cancelAnimationFrame(frameId.current);
  }, []);

  const clamp = (value: number, min: number, max: number): number => 
    Math.max(min, Math.min(value, max));

  const animate = (): void => {
    if (isDownRef.current && isDraggingRef.current && elementRef.current) {
      const parent = elementRef.current.parentElement;

      if (parent) {
        const maxX = parent.clientWidth - elementRef.current.clientWidth;
        const maxY = parent.clientHeight - elementRef.current.clientHeight;

        const newLeft = clamp(position[0] + deltaRef.current[0], 0, maxX);
        const newTop = clamp(position[1] + deltaRef.current[1], 0, maxY);

        setPosition([newLeft, newTop]);

        frameId.current = requestAnimationFrame(animate);
      }
    }
  };

  const handleMouseDown = (e: ReactMouseEvent): void => {
    e.preventDefault();
    isDownRef.current = true;
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
  };

  const handleMouseMove = (e: MouseEvent): void => {
    e.preventDefault();
    if (!isDownRef.current) return;
    isDraggingRef.current = true;
    deltaRef.current = [deltaRef.current[0] + e.movementX, deltaRef.current[1] + e.movementY];
    frameId.current = requestAnimationFrame(animate);
  };

  const handleMouseUp = (e: MouseEvent): void => {
    e.preventDefault();
    isDownRef.current = false;
    isDraggingRef.current = false;
    cancelAnimationFrame(frameId.current);
    if (elementRef.current) {
      setPositionStorage([elementRef.current.offsetLeft, elementRef.current.offsetTop]);
      console.log(positionStorage);
    }
    deltaRef.current = [0, 0];
    window.removeEventListener('mousemove', handleMouseMove);
    window.removeEventListener('mouseup', handleMouseUp);
  };

  return [position, handleMouseDown];
};

export default useMoveElement;
