import React, {use, useEffect} from "react";
import {Outlet, useNavigate} from "react-router-dom";
import {DataContext} from "./DataProvider";

const AuthProtectedRoutes = () => {
  const {isAuthenticated} = use(DataContext);
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate("accounts/login/", { replace: true });
    }
  }, []);

  return <Outlet />;
};

export default AuthProtectedRoutes;
