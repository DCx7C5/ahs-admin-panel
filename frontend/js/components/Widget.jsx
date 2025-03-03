import React, {useRef} from 'react';
import useMoveElement from "../hooks/useMoveElement";


export const Widget = () => {
    const elementRef = useRef(null);
    const [position, handleMouseDown] = useMoveElement(elementRef);

    return (
        <div className="widget"
             ref={elementRef}
             onMouseDown={handleMouseDown}
             style={{left: `${position[0]}px`, top: `${position[1]}px`}}
        >
            <div className="widget-header"><h3>Name</h3></div>
        </div>
    )
}
