import {useCallback, useEffect, useRef, useState} from 'react';
import PropTypes from 'prop-types';



const ReadyState = {
  Connecting: 0,
  Open: 1,
  Closing: 2,
  Closed: 3,
}


export const useWebSocket = (initialEndPoint, options = {}) => {
  return useSocket(initialEndPoint, options);
}



export const useSocket = (initialEndPoint, options = {}) => {
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

  const endPointRef = useRef(initialEndPoint);
  const reconnectTimesRef = useRef(0);
  const reconnectTimerRef = useRef(null);
  const websocketRef = useRef(null);

  const [latestMessage, setLatestMessage] = useState(null);
  const [readyState, setReadyState] = useState(ReadyState.Closed);
  const commandsRef = useRef({});

  const isMounted = useRef(true);

  useEffect(() => {
    isMounted.current = true;
    if (!manual && endPointRef.current) {
      connect();
    }

    return () => {
      isMounted.current = false;
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      disconnect();
    };
  }, []);

  const reconnect = () => {
    if (websocketRef.current && websocketRef.current.readyState === ReadyState.Open) {
      return;
    }

    if (reconnectTimesRef.current < reconnectLimit) {
      clearTimeout(reconnectTimerRef.current);

      reconnectTimerRef.current = setTimeout(() => {
        connectWs();
        reconnectTimesRef.current++;
      }, reconnectInterval);
    } else {
      console.warn('Reconnect limit reached. Stopping further attempts.');
    }
  };

  const connectWs = () => {
    clearTimeout(reconnectTimerRef.current);

    if (websocketRef.current) {
      websocketRef.current.close();
    }

    const proto = document.location.protocol === 'https:' ? 'wss' : 'ws';
    const socketUrl = `${proto}://${window.location.host}/ws/${endPointRef.current}/`;
    const ws = new WebSocket(socketUrl, protocols);
    setReadyState(ReadyState.Connecting);

    ws.onerror = (event) => {
      const error = event.error || event.message;

      if (error && error.includes('Unauthorized')) {
        reconnectTimesRef.current = reconnectLimit;
      } else {
        reconnect();
      }

      if (onError) {
        onError(event, ws);
      }

      if (isMounted.current) setReadyState(ws.readyState || ReadyState.Closed);
    };

    ws.onopen = (event) => {
      if (websocketRef.current !== ws) {
        return;
      }

      if (onOpen) {
        onOpen(event, ws);
      }
      reconnectTimesRef.current = 0;

      if (isMounted.current) {
        setReadyState(ws.readyState || ReadyState.Open);
      }
    };

    ws.onmessage = (message) => {
      if (websocketRef.current !== ws) return;
      const data = JSON.parse(message.data);
      console.log('onMessage', data);

      if (mode === 'channel') {
        const { handler, args } = commandsRef.current[data.app][data.cmd][data.unique_id];
        handler(data.data, ...args);
      } else {
        if (onMessage) {
          onMessage(message, ws);
        }
        if (isMounted.current) {
          setLatestMessage(data);
        }
      }
    };

    ws.onclose = (event) => {
      if (onClose) {
        onClose(event, ws);
      }
      if (websocketRef.current === ws) {
        reconnect();
      }
      if (!websocketRef.current || websocketRef.current === ws) {
        if (isMounted.current) setReadyState(ws.readyState || ReadyState.Closed);
      }
    };

    websocketRef.current = ws;
  };

  const connect = useCallback(() => {
    reconnectTimesRef.current = 0;
    connectWs();
  }, []);

  const disconnect = useCallback(() => {
    clearTimeout(reconnectTimerRef.current);
    reconnectTimesRef.current = reconnectLimit;
    websocketRef.current?.close();
    websocketRef.current = undefined;
  }, [reconnectLimit]);

  const sendMessage = useCallback((message) => {
    if (readyState !== ReadyState.Open) {
      console.warn('WebSocket is not open. Message not sent.');
      return;
    }
    websocketRef.current?.send(message);
  }, [readyState]);

  const changeEndpoint = useCallback((newEndPoint) => {
    console.log(`Changing WebSocket endpoint to: ${newEndPoint}`);
    if (readyState !== ReadyState.Closed) {
      disconnect();
    }
    endPointRef.current = newEndPoint;
    connect();
  }, [disconnect, connect, readyState]);

  const registerMsgCallback = useCallback((app, command, handler, args = [], kwargs = {}, uniqueId = 0) => {
    if (!command || typeof handler !== 'function') {
      console.error('Invalid command or handler');
      return;
    }

    if (!commandsRef.current[app]) {
      commandsRef.current[app] = {};
    }

    if (!commandsRef.current[app][command]) {
      commandsRef.current[app][command] = {};
    }

    commandsRef.current[app][command][uniqueId] = { handler, args, kwargs };
    console.log('Successful registered', commandsRef.current);
  }, []);

  return {
    sendMessage,
    connect,
    disconnect,
    changeEndpoint,
    readyState,
    readyStateString:
      readyState === ReadyState.Connecting
        ? 'Connecting'
        : readyState === ReadyState.Open
        ? 'Open'
        : readyState === ReadyState.Closing
        ? 'Closing'
        : 'Closed',
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

useSocket.PropTypes = {
  latestMessage: PropTypes.any, // Optional, as WebSocketEventMap['message'] isn't directly representable, use any.
  sendMessage: PropTypes.func.isRequired, // This corresponds to WebSocket's `send` method.
  disconnect: PropTypes.func.isRequired, // A required function.
  connect: PropTypes.func.isRequired, // A required function.
  readyState: PropTypes.number.isRequired, // Representing the `ReadyState` enum as a number.
  webSocketIns: PropTypes.instanceOf(WebSocket), // Optional WebSocket instance.
};

export default useSocket;