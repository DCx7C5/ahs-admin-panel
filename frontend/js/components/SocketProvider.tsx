import React, { createContext, ReactNode, useEffect } from "react";
import useSocket from "../hooks/useSocket";


interface SocketContextProps {
  changeEndpoint: (endpoint: string) => void;
  sendMessage: (message: string) => void;
  disconnect: () => void;
  connect: () => void;
  readyState: number;
  readyStateString: string;
  webSocketIns: WebSocket | null;
  registerMsgCallback: (
    app: string,
    command: string,
    callback: (data: any) => void,
    args?: any,
    kwargs?: any,
    uniqueId?: string | number
  ) => void;
}

interface SocketProviderProps {
  children: ReactNode;
  endPoint?: string;
  manual?: boolean;
  reconnectLimit?: number;
  reconnectInterval?: number;
  onError?: (event: Event, ws?: WebSocket) => void;
  onOpen?: (event: Event, ws?: WebSocket) => void;
  onMessage?: (message: MessageEvent, ws?: WebSocket) => void;
  onClose?: (event: CloseEvent, ws?: WebSocket) => void;
  mode?: string;
}

export const SocketContext = createContext<SocketContextProps | undefined>(undefined);

export const SocketProvider: React.FC<SocketProviderProps> = ({
  endPoint = '',
  manual = true,
  reconnectLimit = 10,
  reconnectInterval = 6000,
  mode,
  children,
  onError,
  onOpen,
  onMessage,
  onClose,
}) => {

  const {
    changeEndpoint,
    sendMessage,
    disconnect,
    connect,
    readyState,
    readyStateString,
    webSocketIns,
    registerMsgCallback,
  } = useSocket(endPoint, {
    reconnectLimit,
    reconnectInterval,
    manual,
    mode,
    onError,
    onOpen,
    onMessage,
    onClose,
  });

  return (
    <SocketContext.Provider
      value={{
        changeEndpoint,
        sendMessage,
        disconnect,
        connect,
        readyState,
        readyStateString,
        webSocketIns,
        registerMsgCallback,
      }}
    >
      {children}
    </SocketContext.Provider>
  );
};

export default SocketProvider;