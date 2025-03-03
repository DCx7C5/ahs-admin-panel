import React, {lazy, Suspense} from "react";
import {BrowserRouter, Route, Routes} from "react-router-dom";
import Layout from "./components/Layout/Layout";
import AuthProtectedRoutes from "./components/AuthProtectedRoutes";
import AuthProvider from "./components/AuthProvider";


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
    <AuthProvider>
      <Suspense>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route path="login" element={<Login />} />
              <Route element={<AuthProtectedRoutes />}>
                <Route index element={<DashBoard />} />
                <Route path="dashboard" element={<DashBoard />} />
                <Route path="settings" element={<Settings />} />
                <Route path="logout" element={<Test />} />
              </Route>
            </Route>
          </Routes>
        </BrowserRouter>
      </Suspense>
    </AuthProvider>
  );
};

export default Root;