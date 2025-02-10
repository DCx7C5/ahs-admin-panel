import RestrictedContent from "../components/RestrictedContent";
import React, {lazy, ReactNode, StrictMode, Suspense} from "react";
import DataProvider from "../components/DataProvider";
import SocketProvider from "../components/SocketProvider";



const Terminal = lazy(() =>
  import("../components/Terminal/Terminal").then(module => ({
    default: module.Terminal,
  }))
);


const Base = ({ children }: {children: ReactNode}) => {

  return (
    <DataProvider>
      {children}
      <RestrictedContent>
        <Suspense>
          <Terminal />
        </Suspense>
      </RestrictedContent>
    </DataProvider>
  );
};

export default Base;