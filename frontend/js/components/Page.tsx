import React, {StrictMode, use, useEffect, useState} from 'react';
import ChannelProvider from "./ChannelProvider";
import RestrictedContent from "./RestrictedContent";
import {DataContext, DataContextType} from "./DataProvider";

interface PageProps {
  children: React.ReactNode;
}


export const Page: React.FC<PageProps> = ({children}
) => {
    const { socketUrl, pages } = use<DataContextType>(DataContext);
    const [title, setTitle] = useState(pages[window.location.pathname])

    useEffect(() => {
        console.log("Page | Mounted component with endPoint: ", window.location.pathname);

    }, []);

    return (
        <RestrictedContent>
            <ChannelProvider>
                <StrictMode>
                    <div className="page-header">
                        {title && <h1 className="page-title">{title}</h1>}
                    </div>
                    {children}
                </StrictMode>
            </ChannelProvider>
        </RestrictedContent>
    );
};

export default Page;