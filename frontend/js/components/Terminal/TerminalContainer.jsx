import React, {use, useEffect, useRef, useState} from "react";
import useDragResizeHeight from "../../hooks/useDragResizeHeight";
import {useLocalStorage} from "../../hooks/useStorage";
import {TerminalContext} from "./TerminalDataProvider";
import useClientWidth from "../../hooks/useClientWidth";


const debounce = (func, delay) => {
  let timeoutId;

  return (...args) => {
    // Clear any previously scheduled execution
    if (timeoutId) clearTimeout(timeoutId);

    // Schedule the function to run after the delay
    timeoutId = setTimeout(() => {
      func(...args);
    }, delay);
  };
};

export const TerminalContainer = ({ children }) => {
  const resizableRef = useRef(null);
  const resizerRef = useRef(null);
  const containerRef = useRef(null);
  const [lastHeightStorage, setLastHeightStorage] = useLocalStorage('term.height', 0,);
  const [height, setHeight] = useState(lastHeightStorage);
  const width = useClientWidth(containerRef)
  const {handleResize, readyState} = use(TerminalContext)
  const {onMouseDown} = useDragResizeHeight(
    resizableRef,
    setHeight,
    setLastHeightStorage,
    () => handleResize()
  );
  const debouncedResizeHandler = debounce(() => {
      if (readyState === 1) handleResize();
    }, 666);

  useEffect(() => {

    setHeight(lastHeightStorage)
  }, []);

  useEffect(() => {
    debouncedResizeHandler();
  }, [width]);

  return (
    <>
      <div ref={containerRef} id='terminal-container' >
        <div className='slider' onMouseDown={onMouseDown} >
          <div ref={resizerRef} className="lip" />
        </div>
        <div ref={resizableRef} id='terminal-wrapper' style={{
          height: height + 'px',
          width: width,
          display: 'flex',
          flexDirection: 'column',
        }}>
          {children}
        </div>
      </div>
    </>
  )
}


export default TerminalContainer;