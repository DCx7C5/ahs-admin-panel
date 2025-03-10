import React, {lazy, Suspense, use, useContext} from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from "../Sidebar/Sidebar";
import Navbar from "../Navbar/Navbar";
import {DataContext} from "../DataProvider";


const Terminal = lazy(() =>
  import("../Terminal/Terminal").then(module => ({
    default: module.Terminal,
  }))
);


export const Layout = () => {
  const {isAuthenticated, isSuperUser} = use(DataContext);
  return (
      <div className="app-container">
          <div className="content-wrapper">
            {isAuthenticated ? <Navbar /> : null}
            <main className="main-content" >
                <Outlet />
            </main>
            {isSuperUser ? <Terminal /> : null}
          </div>
      </div>
  );
}

export default Layout;