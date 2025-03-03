import RestrictedContent from "../components/RestrictedContent";
import React, {lazy, ReactNode, StrictMode, Suspense} from "react";



const Terminal = lazy(() =>
  import("../components/Terminal/Terminal").then(module => ({
    default: module.Terminal,
  }))
);


const Base = ({ children }: {children: ReactNode}) => {

  return (
    <>
      {children}

    </>
  );
};

export default Base;