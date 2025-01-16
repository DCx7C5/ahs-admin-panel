import React from "react";
import ReactDOM from "react-dom/client";
import Root from "./Root";
import "../css/base.scss"


const rootElement = document.getElementById("root");
ReactDOM.createRoot(rootElement!).render(<Root />);