import { useCallback, useEffect, useRef, useState } from 'react';

// Define ReadyState as an enum for better TypeScript integration
enum ReadyState {
  Connecting = 0,
  Open = 1,
  Closing = 2,
  Closed = 3,
}

// WebSocket handler types
type WebSocketEventHandler = (event: Event, ws: WebSocket) => void;
type WebSocketMessageHandler = (event: MessageEvent, ws: WebSocket) => void;
type WebSocketErrorHandler = (event: Event, ws: WebSocket) => void;

// Command callback type
type CommandHandler = (data: any, ...args: any[]) => void;

// Command registry structure
interface CommandRegistry {
  [app: string]: {
    [command: string]: {
      [uniqueId: number]: {
        handler: CommandHandler;
        args: any[];
        kwargs: Record<string, any>;
      };
    };
  };
}

// Options interface
interface UseSocketOptions {
  reconnectLimit?: number;
  reconnectInterval?: number;
  manual?: boolean;
  mode?: 'channel' | string;
  onOpen?: WebSocketEventHandler;
  onClose?: WebSocketEventHandler;
  onMessage?: WebSocketMessageHandler;
  onError?: WebSocketErrorHandler;
  protocols?: string | string[];
}

// Return type for useSocket hook
interface UseSocketReturn {
  sendMessage: (message: string) => void;
  connect: () => void;
  disconnect: () => void;
  changeEndpoint: (newEndPoint: string) => void;
  readyState: ReadyState;
  readyStateString: string;
  webSocketIns: WebSocket | undefined;
  registerMsgCallback: (
    app: string,
    command: string,
    handler: CommandHandler,
    args?: any[],
    kwargs?: Record<string, any>,
    uniqueId?: number
  ) => void;
}

/**
 * Alias for useSocket - maintains backward compatibility
 */
export const useWebSocket = (
  initialEndPoint: string,
  options: UseSocketOptions = {}
): UseSocketReturn => {
  return useSocket(initialEndPoint, options);
};

/**
 * A hook for managing WebSocket connections
 * @param initialEndPoint - The initial endpoint for the WebSocket connection
 * @param options - Configuration options for the WebSocket
 */
export const useSocket = (
  initialEndPoint: string,
  options: UseSocketOptions = {}
): UseSocketReturn => {
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

  const endPointRef = useRef<string>(initialEndPoint);
  const reconnectTimesRef = useRef<number>(0);
  const reconnectTimerRef = useRef<number | null>(null);
  const websocketRef = useRef<WebSocket | null>(null);

  const [latestMessage, setLatestMessage] = useState<any>(null);
  const [readyState, setReadyState] = useState<ReadyState>(ReadyState.Closed);
  const commandsRef = useRef<CommandRegistry>({});

  const isMounted = useRef<boolean>(true);

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

  const reconnect = (): void => {
    if (websocketRef.current && websocketRef.current.readyState === ReadyState.Open) {
      return;
    }

    if (reconnectTimesRef.current < reconnectLimit) {
      if (reconnectTimerRef.current !== null) {
        clearTimeout(reconnectTimerRef.current);
      }

      reconnectTimerRef.current = window.setTimeout(() => {
        connectWs();
        reconnectTimesRef.current++;
      }, reconnectInterval);
    } else {
      console.warn('Reconnect limit reached. Stopping further attempts.');
    }
  };

  const connectWs = (): void => {
    if (reconnectTimerRef.current !== null) {
      clearTimeout(reconnectTimerRef.current);
    }

    if (websocketRef.current) {
      websocketRef.current.close();
    }

    const proto = document.location.protocol === 'https:' ? 'wss' : 'ws';
    const socketUrl = `${proto}://${window.location.host}/ws/${endPointRef.current}/`;
    const ws = new WebSocket(socketUrl, protocols);
    setReadyState(ReadyState.Connecting);

    ws.onerror = (event: Event) => {
      const error = (event as any).error || (event as any).message;

      if (error && typeof error === 'string' && error.includes('Unauthorized')) {
        reconnectTimesRef.current = reconnectLimit;
      } else {
        reconnect();
      }

      if (onError) {
        onError(event, ws);
      }

      if (isMounted.current) setReadyState(ws.readyState as ReadyState || ReadyState.Closed);
    };

    ws.onopen = (event: Event) => {
      if (websocketRef.current !== ws) {
        return;
      }

      if (onOpen) {
        onOpen(event, ws);
      }
      reconnectTimesRef.current = 0;

      if (isMounted.current) {
        setReadyState(ws.readyState as ReadyState || ReadyState.Open);
      }
    };

    ws.onmessage = (message: MessageEvent) => {
      if (websocketRef.current !== ws) return;
      const data = JSON.parse(message.data as string);
      console.log('onMessage', data);

      if (mode === 'channel') {
        const app = data.app as string;
        const cmd = data.cmd as string;
        const uniqueId = data.unique_id as number;
        
        if (commandsRef.current[app] && 
            commandsRef.current[app][cmd] && 
            commandsRef.current[app][cmd][uniqueId]) {
          const { handler, args } = commandsRef.current[app][cmd][uniqueId];
          handler(data.data, ...args);
        }
      } else {
        if (onMessage) {
          onMessage(message, ws);
        }
        if (isMounted.current) {
          setLatestMessage(data);
        }
      }
    };

    ws.onclose = (event: CloseEvent) => {
      if (onClose) {
        onClose(event, ws);
      }
      if (websocketRef.current === ws) {
        reconnect();
      }
      if (!websocketRef.current || websocketRef.current === ws) {
        if (isMounted.current) setReadyState(ws.readyState as ReadyState || ReadyState.Closed);
      }
    };

    websocketRef.current = ws;
  };

  const connect = useCallback((): void => {
    reconnectTimesRef.current = 0;
    connectWs();
  }, []);

  const disconnect = useCallback((): void => {
    if (reconnectTimerRef.current !== null) {
      clearTimeout(reconnectTimerRef.current);
    }
    reconnectTimesRef.current = reconnectLimit;
    websocketRef.current?.close();
    websocketRef.current = undefined;
  }, [reconnectLimit]);

  const sendMessage = useCallback((message: string): void => {
    if (readyState !== ReadyState.Open) {
      console.warn('WebSocket is not open. Message not sent.');
      return;
    }
    websocketRef.current?.send(message);
  }, [readyState]);

  const changeEndpoint = useCallback((newEndPoint: string): void => {
    console.log(`Changing WebSocket endpoint to: ${newEndPoint}`);
    if (readyState !== ReadyState.Closed) {
      disconnect();
    }
    endPointRef.current = newEndPoint;
    connect();
  }, [disconnect, connect, readyState]);

  const registerMsgCallback = useCallback((
    app: string,
    command: string,
    handler: CommandHandler,
    args: any[] = [],
    kwargs: Record<string, any> = {},
    uniqueId: number = 0
  ): void => {
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
    console.log('Successfully registered', commandsRef.current);
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
    webSocketIns: websocketRef.current ?? undefined,
    registerMsgCallback,
  };
};

export default useSocket;
