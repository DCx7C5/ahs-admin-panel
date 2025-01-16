import React from 'react';

interface ContentSectionProps {
  children: React.ReactNode;
  title: string;
}

export const ContentSection: React.FC<ContentSectionProps> = (
    {children, title}
) => {
  return (
    <>
      <div className="section-header">{title}</div>
      <div className="section">
        {children}
      </div>
    </>
  )
}


export default ContentSection;