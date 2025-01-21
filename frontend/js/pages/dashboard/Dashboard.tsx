import React, {useEffect} from "react";
import RealTimeClock from "./Clock";
import "@/../css/dash.scss";
import Page from "../../components/Page";
import ContentSection from "../../components/ContentSection";
import Bookmarks from "../../components/Bookmarks/Bookmarks";


export const Dashboard = () => {

  return (
    <div id='dashboard'>
      <Page title={'Dashboard'}
            headerContent={<RealTimeClock/>}
      >
        <ContentSection title={'Bookmarks'}>
          <Bookmarks />
        </ContentSection>
      </Page>
    </div>
  )
}

export default Dashboard;
