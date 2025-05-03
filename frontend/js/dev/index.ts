import React from "react"
import {useInitial} from "./useInitial"

export const ComponentPreviews = React.lazy(() => import("./previews")
    .then(module => ({
        default: module.ComponentPreviews
    })))

export {
    useInitial
}
export default ComponentPreviews;