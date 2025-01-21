import React from 'react';
import { Outlet } from 'react-router-dom';
import Base from "./pages/Base";
import RestrictedContent from "./components/RestrictedContent";
import Sidebar from "./components/Sidebar/Sidebar";
import {PageWrapper} from "./components/Page";


export const Layout = () => {
  return (
    <Base>
      <div className="content-wrapper">
        <Sidebar toggleClass='sbtoggle' />
        <main className="main-content" >
          <RestrictedContent>
            <PageWrapper>
              <Outlet />
            </PageWrapper>
          </RestrictedContent>
        </main>
      </div>
      <footer className="footer"/>
    </Base>
  );
}

export default Layout;