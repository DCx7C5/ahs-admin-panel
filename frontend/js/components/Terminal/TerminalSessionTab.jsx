import React, {use, useEffect, useState} from "react";
import { TerminalContext } from "./TerminalDataProvider";
import { AttachAddon } from "@xterm/addon-attach";
import PropTypes from "prop-types";
import "./css/sessiontab.scss"


export const TerminalSessionTab = ({ session }) => {
  const {
    changeToSession,
    closeSession,
    toggleVisibility,
    webSocketIns,
    getActiveSessionId,

  } = use(TerminalContext);


  useEffect(() => {
    // Attach to WebSocket or manage behavior AFTER session is provided (no creation here).
    if (webSocketIns && session.xterm) {
      if (!session.attachAddon) {
        session.attachAddon = new AttachAddon(webSocketIns);
        session.xterm.loadAddon(session.attachAddon);
      }

      session.xterm.onData((data) => {
        if (data === '\x04') { // Ctrl+D key press
          closeSession(session.id); // Close the session.
          toggleVisibility(); // Optionally toggle the terminal display.
          console.log("Terminal closed via Ctrl+D");
        }
      });
    }
  }, [webSocketIns, session]);

  function handleTabClick() {
    const activeSessionId = getActiveSessionId()
    console.log('handleTabClick', activeSessionId, session.id)
    if (activeSessionId === session.id) return; // No action needed if already the active session.
    changeToSession(session); // Activate the session.
    console.log("Switched to session:", session.name);
  }

  function handleTabClose(event) {
    event.stopPropagation(); // Prevent click events from propagating to the tab container.
    closeSession(session.id)    ; // Close and fully remove the session.
    console.log("Closed session tab:", session.name);
  }


  return (
    <>
      <div
        className={`tab-element tab-button ${session.active ? "active" : ""}`}
        onClick={handleTabClick}
        style={{ borderBottom: session.active ? "none" : null }}
      >
        {session.name}
        <div onClick={handleTabClose} className={"tab-close-button"}>
          ×
        </div>
      </div>
    </>
  );
};

TerminalSessionTab.propTypes = {
  session: PropTypes.shape({
    name: PropTypes.string.isRequired, // Name of the session.
    xterm: PropTypes.object.isRequired, // Associated xterm instance.
    fitAddon: PropTypes.object, // Optional xterm add-ons.
    webglAddon: PropTypes.object,
    serializeAddon: PropTypes.object,
    unicode11Addon: PropTypes.object,
    attachAddon: PropTypes.object,
    webSocketIns: PropTypes.object, // WebSocket connection associated with the session.
    state: PropTypes.any, // Serialized terminal state (string, buffer, or null).
    fit: PropTypes.func, // Function to resize the terminal.
    onDispose: PropTypes.func, // Callback when the session is disposed.
  }).isRequired, // Enforce the session prop structure.
};

export default TerminalSessionTab;