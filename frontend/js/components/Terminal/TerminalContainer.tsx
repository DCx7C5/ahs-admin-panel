import React, { useEffect, useRef, useState, ReactNode } from "react";
import useDragResizeHeight from "../../hooks/useDragResizeHeight";
import { useLocalStorage } from "../../hooks/useStorage";
import { TerminalContext } from "./TerminalDataProvider";
import useClientWidth from "../../hooks/useClientWidth";

// Define the debounce utility function with types
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


// Define props type for TerminalContainer
interface TerminalContainerProps {
  children: ReactNode;
}

export const TerminalContainer: React.FC<TerminalContainerProps> = ({ children }) => {
  const resizableRef = useRef<HTMLDivElement | null>(null);
  const resizerRef = useRef<HTMLDivElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  // Use the useLocalStorage hook with initial typing
  const [lastHeightStorage, setLastHeightStorage] = useLocalStorage<number>('term.height', 0);
  const [height, setHeight] = useState<number>(lastHeightStorage);
  const width = useClientWidth(containerRef);

  const { handleResize, readyState } = React.useContext(TerminalContext);
  const { onMouseDown } = useDragResizeHeight(
    resizableRef,
    setHeight,
    setLastHeightStorage,
    () => handleResize()
  );

  const debouncedResizeHandler = debounce(() => {
    if (readyState === 1) handleResize();
  }, 666);

  useEffect(() => {
    setHeight(lastHeightStorage);
  }, [lastHeightStorage]);

  useEffect(() => {
    debouncedResizeHandler();
  }, [width]);

  return (
    <>
      <div ref={containerRef} id="terminal-container">
        <div className="slider" onMouseDown={onMouseDown}>
          <div ref={resizerRef} className="lip" />
        </div>
        <div
          ref={resizableRef}
          id="terminal-wrapper"
          style={{
            height: height + "px",
            width: width,
            display: "flex",
            flexDirection: "column",
          }}
        >
          {children}
        </div>
      </div>
    </>
  );
};

export default TerminalContainer;