import React, {createContext, ReactNode} from "react";
import useWebSocket from "../hooks/useWebsocket";


interface SocketContextProps {
  sendMessage: (message: string) => void;
  disconnect: () => void;
  connect: () => void;
  readyState: number;
  webSocketIns: WebSocket | null;
  registerMsgCallback: (
    app: string,
    command: string,
    callback: (data: any) => void,
    kwargs?: any,
    uniqueId?: string
  ) => void;
}


interface SocketProviderProps {
  endPoint: string;
  manual?: boolean;
  reconnectLimit?: number;
  reconnectInterval?: number;
  children: ReactNode;
  onError?: (event: Event) => void;
  onOpen?: (event: Event) => void;
  onClose?: (event: CloseEvent) => void;
  mode?: string;
}


export const SocketContext = createContext<SocketContextProps | undefined>(undefined);



export const SocketProvider: React.FC<SocketProviderProps> = ({
  endPoint,
  manual = true,
  reconnectLimit = 10, // Default value
  reconnectInterval = 6000,
  mode,
  children,
}) => {
  const {
    sendMessage,
    disconnect,
    connect,
    readyState,
    webSocketIns,
    registerMsgCallback
  } = useWebSocket(endPoint, {
    reconnectLimit,
    reconnectInterval,
    manual,
    mode,
  });


  return <SocketContext.Provider value={{
    sendMessage,
    disconnect,
    connect,
    readyState,
    webSocketIns,
    registerMsgCallback,
  }}>
    {children}
  </SocketContext.Provider>;
};

export default SocketProvider;