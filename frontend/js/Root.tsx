import React, {lazy, Suspense} from "react";
import {BrowserRouter, Route, Routes} from "react-router-dom";
import DataProvider from "./components/DataProvider";
import PageSuspenseSpinner from "./components/Spinner";

const AuthProtectedRoutes = lazy(() => import("./components/AuthProtectedRoutes")
    .then(module => ({
        default: module.AuthProtectedRoutes
    }))
);

const Layout = lazy(() => import("./components/Layout/Layout")
    .then(module => ({
        default: module.Layout,
    }))
);

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
      <Suspense fallback={<PageSuspenseSpinner />}>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route path="test2/" element={<Test />} />
              <Route path="accounts/login/" element={<Login />} />
              <Route path="accounts/signup/" element={<SignUp />} />
              <Route element={<AuthProtectedRoutes />}>
                <Route index element={<DashBoard />} />
                <Route path="test/" element={<Test />} />
                <Route path="dashboard/" element={<DashBoard />} />
                <Route path="settings/" element={<Settings />} />
              </Route>
            </Route>
          </Routes>
        </BrowserRouter>
      </Suspense>
    </DataProvider>
  );
};

export default Root;