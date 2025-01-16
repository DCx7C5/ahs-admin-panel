import React from 'react';

interface PageProps {
  children: React.ReactNode;
  title: string;
  headerContent: React.ReactNode;
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


export default Page;