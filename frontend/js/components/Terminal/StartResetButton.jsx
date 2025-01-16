import React, {use} from "react";
import {TerminalContext} from "./TerminalDataProvider";

export const StartResetButton = () => {
  const { closeSession, createSession, activeSessionId, sessions } = use(TerminalContext)


  const handleClick = () => {
    if (sessions.length > 0 ) {
      closeSession(activeSessionId)

      createSession()
    } else {
      createSession()
    }
  }

  return (
    <button id="start-btn" className="tab-element ctrl-button btn" onClick={handleClick}>
      <i className={`bi ${sessions.length !== 0 ? 'bi-arrow-repeat' : 'bi-play-fill'}`}
         style={{fontWeight: 'bold'}}
      ></i>
    </button>
  )
}
export default StartResetButton;