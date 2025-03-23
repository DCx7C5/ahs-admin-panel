import React, {lazy, Suspense} from "react";
import {BrowserRouter, Route, Routes} from "react-router-dom";
import Layout from "./components/Layout/Layout";
import AuthProtectedRoutes from "./components/AuthProtectedRoutes";
import DataProvider from "./components/DataProvider";


const DashBoard = lazy(() => import("./pages/Dashboard")
    .then(module => ({
        default: module.Dashboard,
    }))
);

const Login = lazy(() => import("./pages/Login")
    .then(module => ({
        default: module.Login,
    }))
);

const SignUp = lazy(() => import("./pages/Signup")
    .then(module => ({
        default: module.Signup,
    }))
)

const Test = lazy(() => import("./pages/Test")
    .then(module => ({
        default: module.Test,
    }))
);

const Settings = lazy(() => import("./pages/Settings")
    .then(module => ({
        default: module.Settings,
    }))
);


export const Root = () => {


  return (
    <DataProvider>
        <Suspense>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Layout />}>
                <Route path="accounts/login/" element={<Login />} />
                <Route path="accounts/signup/" element={<SignUp />} />
                <Route path="test/" element={<Test />} />
                <Route element={<AuthProtectedRoutes />}>
                  <Route index element={<DashBoard />} />
                  <Route path="dashboard/" element={<DashBoard />} />
                  <Route path="settings/" element={<Settings />} />
                  <Route path="*" element={<Test />} />
                </Route>
              </Route>
            </Routes>
          </BrowserRouter>
        </Suspense>
    </DataProvider>
  );
};

export default Root;