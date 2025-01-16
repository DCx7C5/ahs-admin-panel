import {useRef, useState} from "react";
import useEventListener from "./useEventListener";


const useDragResizeHeight = (resizable, setHeight, setLastHeightStorage, callbackFunc = null) => {
  const [isDown, setIsDown] = useState(false);
  const lastY = useRef(0);

  const handleMouseMove = e => {
    e.preventDefault();
    const viewPortHeight = window.innerHeight
    if (isDown && resizable.current) {
      const realHeight = resizable.current.style.height
      callbackFunc && callbackFunc()
      const deltaY = viewPortHeight - e.y;
      if (deltaY < 0 && (parseInt(realHeight) === 0)) {
        setHeight(0)
        lastY.current = 0
      } else {
        setHeight(deltaY)
        lastY.current = deltaY
      }
    }
  }

  useEventListener('mousemove', handleMouseMove)

  const onMouseDown = e => {
    setIsDown(true);
    e.preventDefault();
    resizable.current.style.cursor = 'row-resize'
    window.addEventListener('mouseup', handleMouseUp)
  }

  const handleMouseUp = e => {
    e.preventDefault()
    setIsDown(false)
    setLastHeightStorage(lastY.current)
    resizable.current.style.cursor = null
    window.removeEventListener('mouseup', handleMouseUp)
  }
  return {onMouseDown}
}

export default useDragResizeHeight