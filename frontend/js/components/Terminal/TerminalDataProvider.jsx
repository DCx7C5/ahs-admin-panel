import React, {createContext, useRef} from 'react';
import useHideElement from "../../hooks/useHideElement";
import useSocket from "../../hooks/useSocket";
import {useTerminalManager} from "../../hooks/useTerminalManager";

export const TerminalContext = createContext(null);



export const TerminalProvider = ({ children }) => {
  const [isVisible,,, toggleVisibility] = useHideElement(false,'term.show')

  const xtermRef = useRef({term: null, fitAddon: null, webglAddon: null})
  const contentRef = useRef(null);

  const {
    connect,
    disconnect,
    webSocketIns,
    readyState,
  } = useSocket(
    `terminal/pty0/`,
    {
      reconnectLimit: 10,
      reconnectInterval: 10000,
      manual: true,
      onOpen: handleSocketOpen,
    }
  );

  const {
    sessions,
    createSession,
    changeToSession,
    handleResize,
    closeSession,
    getSessionById,
    getActiveSession,
    getActiveSessionId,
  } = useTerminalManager(
    {maxSessions: 10, webSocketIns, connect, disconnect, contentRef}
  );



  function handleSocketOpen(event) {
    const session = sessions[sessions.length - 1]  // Get last session in array
    handleResize()
    event.target.send(`stty rows ${session.xterm.rows} cols ${session.xterm.cols}\n`)
    session.xterm.clear()
    changeToSession(session.id, getActiveSession())
    console.log('WebSocket opened', session)
  }


  return (
    <TerminalContext.Provider
      value={{
        sessions,
        xtermRef,
        getActiveSession,
        getActiveSessionId,
        getSessionById,
        createSession,
        changeToSession,
        closeSession,
        connect,
        disconnect,
        webSocketIns,
        readyState,
        toggleVisibility,
        isVisible,
        contentRef,
        handleResize,
      }}
    >
      {children}
    </TerminalContext.Provider>
  );
};

export default TerminalProvider;