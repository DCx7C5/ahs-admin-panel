import RestrictedContent from "../components/RestrictedContent";
import React, {lazy, ReactNode, StrictMode, Suspense} from "react";
import DataProvider from "../components/DataProvider";



const Terminal = lazy(() =>
  import("../components/Terminal/Terminal").then(module => ({
    default: module.Terminal,
  }))
);


const Base = ({ children }: {children: ReactNode}) => {

  return (
    <DataProvider userElementId={'user-data'}
                  menuElementId={'menu-data'}
    >
      <StrictMode>
        {children}
      </StrictMode>
      <RestrictedContent>
        <Suspense>
          <Terminal />
        </Suspense>
      </RestrictedContent>
    </DataProvider>
  );
};

export default Base;