import React from "react";
import RealTimeClock from "./Clock";
import "@/../css/dash.scss";
import Page from "../../components/Page";
import ContentSection from "../../components/ContentSection";
import Bookmarks from "../../components/Bookmarks/Bookmarks";
import SocketProvider from "../../components/SocketProvider";


export const Dashboard = () => {
  return (
    <SocketProvider endPoint='dashboard/' manual={false} mode='dashboard'>
      <div id='dashboard'>
        <Page title={'Dashboard'}
              headerContent={<RealTimeClock/>}
        >
          <ContentSection title={'Bookmarks'}>
            <Bookmarks />
          </ContentSection>
        </Page>
      </div>
    </SocketProvider>
  )
}

export default Dashboard;
