import React, {StrictMode} from "react";
import ReactDOM from "react-dom/client";
import Root from "./Root";
import "../css/base.scss"
import {DevSupport} from "@react-buddy/ide-toolbox";
import ComponentPreviews from "./dev/previews";
import {useInitial} from "./dev";


ReactDOM.createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <DevSupport ComponentPreviews={ComponentPreviews}
                    useInitialHook={useInitial}
        >
            <Root />
        </DevSupport>
    </StrictMode>
);