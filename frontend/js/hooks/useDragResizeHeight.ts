import { useRef, useState, RefObject, MouseEvent as ReactMouseEvent } from "react";
import useEventListener from "./useEventListener";

type CallbackFunc = (() => void) | null;

type UseDragResizeHeightReturn = {
  onMouseDown: (e: ReactMouseEvent<Element, MouseEvent>) => void;
};

const useDragResizeHeight = (
  resizable: RefObject<HTMLElement>,
  setHeight: (height: number) => void,
  setLastHeightStorage: (height: number) => void,
  callbackFunc: CallbackFunc = null
): UseDragResizeHeightReturn => {
  const [isDown, setIsDown] = useState<boolean>(false);
  const lastY = useRef<number>(0);

  const handleMouseMove = (e: MouseEvent) => {
    e.preventDefault();
    const viewPortHeight = window.innerHeight;
    if (isDown && resizable.current) {
      const realHeight = resizable.current.style.height;
      if (callbackFunc) callbackFunc();
      const deltaY = viewPortHeight - e.y;
      if (deltaY < 0 && parseInt(realHeight) === 0) {
        setHeight(0);
        lastY.current = 0;
      } else {
        setHeight(deltaY);
        lastY.current = deltaY;
      }
    }
  };

  useEventListener('mousemove', handleMouseMove);

  const onMouseDown = (e: ReactMouseEvent<Element, MouseEvent>) => {
    setIsDown(true);
    e.preventDefault();
    if (resizable.current) {
      resizable.current.style.cursor = 'row-resize';
    }
    window.addEventListener('mouseup', handleMouseUp);
  };

  const handleMouseUp = (e: MouseEvent) => {
    e.preventDefault();
    setIsDown(false);
    setLastHeightStorage(lastY.current);
    if (resizable.current) {
      resizable.current.style.cursor = '';
    }
    window.removeEventListener('mouseup', handleMouseUp);
  };

  return { onMouseDown };
};

export default useDragResizeHeight;