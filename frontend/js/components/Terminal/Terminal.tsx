import React, { lazy, Suspense, use } from "react";
import TerminalContent from "./TerminalContent";
import TerminalTaskbar from "./TerminalTaskbar";
import TerminalProvider, { TerminalContext } from "./TerminalDataProvider";
import TerminalToggleButton from "./TerminalToggleButton";
import './css/index.scss';

// Lazy-loaded TerminalContainer with module types
const TerminalContainer = lazy(() =>
  import('./TerminalContainer').then((module) => ({
    default: module.TerminalContainer,
  }))
);

// Type definition for the TerminalContext
type TerminalContextType = {
  isVisible: boolean;
};

export const _Terminal: React.FC = () => {
  const { isVisible } = use(TerminalContext as React.Context<TerminalContextType>);

  return (
    <>
      <Suspense fallback={null}> {/* Add a fallback UI for better handling */}
        {isVisible && (
          <TerminalContainer>
            <TerminalTaskbar />
            <TerminalContent />
          </TerminalContainer>
        )}
      </Suspense>
      <TerminalToggleButton />
    </>
  );
};

export const Terminal: React.FC = () => {
  return (
    <TerminalProvider>
      <_Terminal />
    </TerminalProvider>
  );
};

export default Terminal;