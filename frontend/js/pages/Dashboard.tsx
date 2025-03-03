import React from "react";
import RealTimeClock from "../components/Clock";
import "@/../css/dash.scss";
import Page from "../components/Page";
import ContentSection from "../components/ContentSection";
import Bookmarks from "../components/Bookmarks/Bookmarks";


export const Dashboard = () => {

  return (
    <div id='dashboard'>
      <Page>
        <ContentSection title={'Bookmarks'}>
          <Bookmarks />
        </ContentSection>
      </Page>
    </div>
  )
}

export default Dashboard;
