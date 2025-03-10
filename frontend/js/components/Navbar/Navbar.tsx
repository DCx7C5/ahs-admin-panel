import React, {use, useEffect} from "react";
import SidebarToggleButton from "./SidebarToggleButton";
import {DataContext} from "../DataProvider";


export const Navbar = () => {
  const { isAuthenticated, logout } = use(DataContext);

    useEffect(() => {
        console.log("Navbar | Init | Mounted component");

        return () => {
            console.log("Navbar | Unmounted component");
        }
    }, []);

  return (
      <nav id="{{ id }}" className="navbar navbar-default navbar-static-top {{ fixed }}" role="navigation">
        <div className="navinner container-fluid d-flex justify-content-between align-items-center">
          <SidebarToggleButton />
          <div id="breadcrumbs"></div>
          <ul className="navbar-nav ms-auto">
            {
              isAuthenticated
                  ? <li className="nav-item">
                      <a className="nav-link"
                         href="#"
                         onClick={logout}
                      >Logout
                      </a>
                    </li>
                  : null
            }
          </ul>
        </div>
      </nav>
  )
}

export default Navbar;