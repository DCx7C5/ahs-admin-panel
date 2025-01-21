import RestrictedContent from "../components/RestrictedContent";
import React, {lazy, ReactNode, StrictMode, Suspense} from "react";
import AhsDataProvider from "../components/AhsDataProvider";
import SocketProvider from "../components/SocketProvider";



const Terminal = lazy(() =>
  import("../components/Terminal/Terminal").then(module => ({
    default: module.Terminal,
  }))
);


const Base = ({ children }: {children: ReactNode}) => {

  return (
    <AhsDataProvider>
      <StrictMode>
        <SocketProvider>
          {children}
        </SocketProvider>
      </StrictMode>
      <RestrictedContent>
        <Suspense>
          <Terminal />
        </Suspense>
      </RestrictedContent>
    </AhsDataProvider>
  );
};

export default Base;