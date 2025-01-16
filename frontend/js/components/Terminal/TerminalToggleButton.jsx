import React, {use, useRef} from "react";
import useMoveElementVertical from "../../hooks/useMoveElementVertical";
import {TerminalContext} from "./TerminalDataProvider";


const TerminalToggleButton = () => {
  const elementRef = useRef(null);
  const { toggleVisibility } = use(TerminalContext)
  const [top, onMouseDown, onMouseClick] = useMoveElementVertical(
    elementRef,
    'vertical',
    toggleVisibility,
    60
  );

  return (
    <div id='terminal-toggle'>
      <i ref={elementRef}
         onMouseDown={onMouseDown}
         onClick={onMouseClick}
         id='terminal-toggle-btn'
         className='bi bi-terminal'
         style={{top: top + 'px'}}
      />
    </div>
  )
};

export default TerminalToggleButton;
