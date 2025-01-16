import React, {lazy, Suspense} from "react";
import {BrowserRouter, Route, Routes} from "react-router-dom";
import Layout from "./components/Layout";


const DashBoard = lazy(() => import("./pages/dashboard/Dashboard")
    .then(module => ({
        default: module.Dashboard
    }))
);


const Test = () => {
    return (
        <div>
            <h1>Test Page</h1>            
            <h1>Test Page</h1>
            <h1>Test Page</h1>
            <h1>Test Page</h1>

        </div>
    )
}


export const Root = () => {

    return (
        <Suspense>
            <BrowserRouter>
                <Routes>
                    <Route path="/" element={<Layout />} >
                        <Route index element={<DashBoard />} />
                        <Route path='xapi' element={<Test />} >
                            <Route path='settings' element={<Test />} />
                        </Route>
                        <Route path='settings' element={<Test />} />
                    </Route>
                </Routes>
            </BrowserRouter>
        </Suspense>
    )
}

export default Root;