import React, {lazy, Suspense, use} from "react";
import TerminalContent from "./TerminalContent";
import TerminalTaskbar from "./TerminalTaskbar";
import TerminalProvider, {TerminalContext} from "./TerminalDataProvider";
import TerminalToggleButton from "./TerminalToggleButton";
import './css/index.scss';


const TerminalContainer = lazy(() =>
  import('./TerminalContainer').then((module) => ({
    default: module.TerminalContainer,
  }))
);

export const _Terminal = () => {
  const { isVisible } = use(TerminalContext);

  return (<>
    <Suspense>  {/* Lazy-load the TerminalContainer when toggled */}
      {isVisible &&
        <TerminalContainer>
          <TerminalTaskbar/>
          <TerminalContent/>
        </TerminalContainer>
      }
    </Suspense>
    <TerminalToggleButton />
  </>);
};


export const Terminal = () => {
  return <TerminalProvider><_Terminal /></TerminalProvider>
}


export default Terminal;