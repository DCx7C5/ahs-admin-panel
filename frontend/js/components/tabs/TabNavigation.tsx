import React, {Fragment, Suspense, useState, useTransition} from "react";
import TabButton from "./TabButton";


export interface TabNavigationProps {
    tabs: string[];
    activeTab: string;
    setActiveTab: (value: string) => void
}



export const TabNavigation: React.FC<TabNavigationProps> = ({tabs, activeTab, setActiveTab}) => {

    return (
        <>
            <div className="tab-navigation">
                {tabs.map((name, index) => (
                    <Fragment key={index}>
                        <TabButton action={() => setActiveTab(name)}
                                   isActive={activeTab === name}
                        >
                            {name}
                        </TabButton>
                    </Fragment>
                ))}
            </div>
        </>
    )
}


export default TabNavigation;