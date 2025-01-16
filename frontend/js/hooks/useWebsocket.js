import {useCallback, useEffect, useRef, useState} from 'react';
import PropTypes from 'prop-types';



const ReadyState = {
  Connecting: 0,
  Open: 1,
  Closing: 2,
  Closed: 3,
}


export const useWebSocket =(endPoint, options = {}) => {
  const {
    reconnectLimit = 3,
    reconnectInterval = 3 * 1000,
    manual = false,
    mode = undefined,
    onOpen,
    onClose,
    onMessage,
    onError,
    protocols,
  } = options;

  const onOpenRef = useRef(onOpen);
  const onCloseRef = useRef(onClose);
  const onMessageRef = useRef(onMessage);
  const onErrorRef = useRef(onError);

  const reconnectTimesRef = useRef(0);
  const reconnectTimerRef = useRef(null);
  const websocketRef = useRef(null);

  const [latestMessage, setLatestMessage] = useState(null);
  const [readyState, setReadyState] = useState(ReadyState.Closed);
  const commandsRef = useRef({});


  // Track the mounted state of the component
  const isMounted = useRef(true);

  useEffect(() => {
    isMounted.current = true;

    if (!manual && endPoint) {
      connect();
    }

    return () => {
      isMounted.current = false;
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      disconnect();
    };
  },[])

  const reconnect = () => {
    if (websocketRef.current && websocketRef.current.readyState === ReadyState.Open) {
      return; // If the current WebSocket is already open, no need to reconnect
    }

    if (reconnectTimesRef.current < reconnectLimit) {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current); // Clear any previous timers
      }

      reconnectTimerRef.current = setTimeout(() => {
        connectWs();
        reconnectTimesRef.current++;
      }, reconnectInterval);
    } else {
      console.warn('Reconnect limit reached. Stopping further attempts.');
    }
  };

  const connectWs = () => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
    }

    if (websocketRef.current) {
      websocketRef.current.close();
    }
    const proto = document.location.protocol === "https:" ? "wss" : "ws";
    const socketUrl = `${proto}://${window.location.host}/ws/${endPoint}`
    const ws = new WebSocket(socketUrl, protocols);
    setReadyState(ReadyState.Connecting);

    ws.onerror = (event) => {
      const error = event.error || event.message;

      // Example adjustment: Stop reconnecting if the error is related to authentication
      if (error && error.includes("Unauthorized")) {
        reconnectTimesRef.current = reconnectLimit; // Stop reconnects
      } else {
        reconnect(); // Retry for all other errors
      }

      onErrorRef.current?.(event, ws);

      if (isMounted.current) setReadyState(ws.readyState || ReadyState.Closed);
    };

    ws.onopen = (event) => {
      if (websocketRef.current !== ws) {
        return;
      }
      onOpenRef.current?.(event, ws);
      reconnectTimesRef.current = 0;

      // Prevent state updates if the component is unmounted
      if (isMounted.current) {
        setReadyState(ws.readyState || ReadyState.Open)
      }
    };

    ws.onmessage = (message) => {
      if (websocketRef.current !== ws) return;
      const d = JSON.parse(message.data);
      console.log('onMessage', d)
      if (mode === 'dashboard') {
        if (d.uniqueId) {
          const { handler, args } = commandsRef.current[d.app][d.cmd][d.uniqueId];
          handler(d.data, ...args);
        } else {
          const { handler } = commandsRef.current[d.app][d.cmd];
          handler(d.data);
        }
      } else {
        onMessageRef.current?.(message, ws);
        if (isMounted.current) {
          setLatestMessage(d);
        }
      }
    };

    ws.onclose = (event) => {
      onCloseRef.current?.(event, ws);
      if (websocketRef.current === ws) {
        reconnect();
      }
      if (!websocketRef.current || websocketRef.current === ws) {
        // Prevent state updates if the component is unmounted
        if (isMounted.current) setReadyState(ws.readyState || ReadyState.Closed);
      }
    };

    websocketRef.current = ws;
  };

  const readyStateString =
    readyState === ReadyState.Connecting
      ? "Connecting"
      : readyState === ReadyState.Open
      ? "Open"
      : readyState === ReadyState.Closing
      ? "Closing"
      : "Closed";

  const sendMessage = useCallback((message) => {
    if (readyState !== ReadyState.Open) {
      console.warn('WebSocket is not open. Message not sent.');
      return;
    }
    websocketRef.current?.send(message);
  },[]);

  const connect = useCallback(() => {
    reconnectTimesRef.current = 0;
    connectWs();
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
    }
    reconnectTimesRef.current = reconnectLimit;
    websocketRef.current?.close();
    websocketRef.current = undefined;
  }, []);

  const registerMsgCallback = useCallback((app, command, handler, kwargs, uniqueId = undefined) => {
    if (!command || typeof handler !== "function") {
      console.error("Invalid command or handler");
      return;
    }
    if (!commandsRef.current[app]) {
      commandsRef.current[app] = {};
    }

    if (!commandsRef.current[app][command]) {
      commandsRef.current[app][command] = {};
    }

    // Save the handler and its arguments by command
    if (uniqueId) {
      commandsRef.current[app][command][uniqueId] = { handler, kwargs };
    }
    commandsRef.current[app][command] = { handler };
    console.log('Successful registered', commandsRef.current)
  }, [commandsRef]);

  return {
    latestMessage,
    sendMessage,
    connect,
    disconnect,
    readyState,
    readyStateString,
    webSocketIns: websocketRef.current,
    registerMsgCallback,
  };
};

/*
options.PropTypes = {
  reconnectLimit: PropTypes.number, // Optional number
  reconnectInterval: PropTypes.number, // Optional number
  manual: PropTypes.bool, // Optional boolean
  onOpen: PropTypes.func, // Optional function (event callback)
  onClose: PropTypes.func, // Optional function (event callback)
  onMessage: PropTypes.func, // Optional function (event callback)
  onError: PropTypes.func, // Optional function (event callback)
  protocols: PropTypes.oneOfType([
    PropTypes.string, // Can be a string
    PropTypes.arrayOf(PropTypes.string), // Or an array of strings
  ]), // Optional
};
*/

useWebSocket.PropTypes = {
  latestMessage: PropTypes.any, // Optional, as WebSocketEventMap['message'] isn't directly representable, use any.
  sendMessage: PropTypes.func.isRequired, // This corresponds to WebSocket's `send` method.
  disconnect: PropTypes.func.isRequired, // A required function.
  connect: PropTypes.func.isRequired, // A required function.
  readyState: PropTypes.number.isRequired, // Representing the `ReadyState` enum as a number.
  webSocketIns: PropTypes.instanceOf(WebSocket), // Optional WebSocket instance.
};

export default useWebSocket;