import React from "react";
import RealTimeClock from "../components/Clock";
import ContentSection from "../components/ContentSection";
import Bookmarks from "../components/Bookmarks/Bookmarks";
import "@/../css/dash.scss";


export const Dashboard = () => {

  return (
    <div id='dashboard'>
        <ContentSection title={'Clock'} >
            <RealTimeClock />
        </ContentSection>

    </div>
  )
}

export default Dashboard;
