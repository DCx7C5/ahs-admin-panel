import React, {use} from "react";
import {TerminalContext} from "./TerminalDataProvider";

export const StopButton = () => {
  const { sessions, closeSession, getActiveSessionId } = use(TerminalContext);

  function handleClick() {
    const activeSessionId = getActiveSessionId()
    closeSession(activeSessionId)
  }

  return (
    <button id="stop-btn"
            className="tab-element ctrl-button btn"
            disabled={sessions.length === 0}
            onClick={handleClick}
    >
      <i className={"bi bi-stop-fill"} ></i>
    </button>
  )
}
export default StopButton;