import { useEffect, useRef, useState, RefObject, MouseEvent } from "react";
import useEventListener from "./useEventListener";
import { useLocalStorage } from "./useStorage";

// Coordinates interface to type the ref object
interface Coordinates {
  lastTop: number;
  mouseStartY: number;
  distanceTop: number;
}

// Type for the element ref
type ElementRef = RefObject<HTMLElement>;

// Direction type for the useMoveElementVertical hook
type Direction = 'both' | 'vertical' | 'horizontal';

// Return type for the hook
type UseMoveElementVerticalReturn = [
  number,                             // topDistance
  (e: MouseEvent<HTMLElement>) => void, // onMouseDown
  () => void                          // onMouseClick
];

/**
 * A hook that enables vertical dragging of an element
 * @param ref - Reference to the DOM element to be moved
 * @param direction - Direction of movement, defaults to 'both'
 * @param handleClick - Optional click handler
 * @param minTop - Minimum top position, defaults to 0
 * @returns An array containing [topDistance, onMouseDown, onMouseClick]
 */
const useMoveElementVertical = (
  ref: ElementRef,
  direction: Direction = 'both',
  handleClick: (() => void) | null = null,
  minTop: number = 0
): UseMoveElementVerticalReturn => {
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [isDown, setIsDown] = useState<boolean>(false);
  const [positionTopinStorage, setPositionTopinStorage] = useLocalStorage<number>(
    'term.btn.pos', window.innerHeight / 2
  );
  const [topDistance, setTopDistance] = useState<number>(positionTopinStorage);
  const coords = useRef<Coordinates>({
    lastTop: 0,
    mouseStartY: 0,
    distanceTop: 0,
  });

  useEffect(() => {
    coords.current.lastTop = positionTopinStorage;
    setTopDistance(positionTopinStorage);
  }, [positionTopinStorage]);

  const handleMouseMove = (e: MouseEvent): void => {
    e.preventDefault();
    if (isDown && ref.current) {
      setIsDragging(true);
      const deltaY = e.pageY - coords.current.mouseStartY;

      let ntopDistance = coords.current.distanceTop + deltaY;

      const mintoTop = minTop;
      const maxtoTop = window.innerHeight - ref.current.offsetHeight;
      coords.current.lastTop = ntopDistance = Math.max(mintoTop, Math.min(ntopDistance, maxtoTop));

      setTopDistance(ntopDistance);
    }
  };

  useEventListener('mousemove', handleMouseMove);

  const onMouseClick = (): void => {
    if (!isDragging && handleClick) handleClick();
  };

  const onMouseDown = (e: MouseEvent<HTMLElement>): void => {
    setIsDown(true);
    e.preventDefault();
    coords.current.mouseStartY = e.pageY;
    if (ref.current) {
      coords.current.distanceTop = ref.current.offsetTop;
    }
    window.addEventListener('mouseup', handleMouseUp);
  };

  const handleMouseUp = (e: MouseEvent): void => {
    e.preventDefault();
    setTimeout(() => setIsDragging(false), 100);
    setIsDown(false);
    coords.current.lastTop !== 0 && setPositionTopinStorage(coords.current.lastTop);
    window.removeEventListener('mouseup', handleMouseUp as unknown as EventListener);
  };

  return [topDistance, onMouseDown, onMouseClick];
};

export default useMoveElementVertical;
