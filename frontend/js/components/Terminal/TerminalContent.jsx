import React, {use} from "react";
import {TerminalContext} from "./TerminalDataProvider";



const TerminalContent = () => {
  const {contentRef} = use(TerminalContext);



  return <div ref={contentRef} className={`term-content`} />;
};


export default TerminalContent;