import React from 'react';
import { Outlet } from 'react-router-dom';
import Base from "../pages/Base";
import RestrictedContent from "./RestrictedContent";
import Sidebar from "./Sidebar/Sidebar";


export const Layout = () => {

  return (
    <Base>
      <div className="content-wrapper">
        <Sidebar toggleClass='sbtoggle' />
        <main className="main-content" >
          <RestrictedContent>
            <Outlet/>
          </RestrictedContent>
        </main>
      </div>
      <footer className="footer"/>
    </Base>
  );
}

export default Layout;