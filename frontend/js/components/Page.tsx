import React, {use, useEffect} from 'react';
import {DataContext} from "./AhsDataProvider";
import SocketProvider from "./SocketProvider";

interface PageProps {
  children: React.ReactNode;
  title: string;
  headerContent: React.ReactNode;
}

interface PageWrapperProps {
  children: React.ReactNode;
}


export const Page: React.FC<PageProps> = (
    {
      children,
      title = null,
      headerContent = null,
    }
) => {
  return (
    <>
      <div className="page-header">
        {headerContent || (title && <h1 className="page-title">{title}</h1>)}
      </div>
      {children}
    </>
  );
};

export const PageWrapper: React.FC<PageWrapperProps> = ({children}) => {
  const { socketUrl } = use(DataContext);

  useEffect(() => {
    console.log("PAGE WRAPPER MOUNTED", socketUrl)
  }, [socketUrl]);

  return (
    <SocketProvider
        endPoint={socketUrl}
        manual={false}
        mode='channel'
    >
      {children}
    </SocketProvider>
  );
};

export default Page;