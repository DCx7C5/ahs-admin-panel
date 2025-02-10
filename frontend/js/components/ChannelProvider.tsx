import React, {createContext, use, useEffect} from "react";
import useChannelLayer from "../hooks/useChannelLayer";
import { DataContext } from "./DataProvider";

interface ChannelContextProps {
  connect: () => void;
  disconnect: () => void;
  readyState: number;
  registerCommand: (input: { command_name: string; command: string; callback: (data: any) => void }) => void;
  sendCommand: (command: string, data: any) => void;
  socketUrl: string;
}

interface ChannelProviderProps {
  children: React.ReactNode;
}

export const ChannelContext = createContext<ChannelContextProps | undefined>(undefined);

export const ChannelProvider: React.FC<ChannelProviderProps> = ({ children }) => {
  const { socketUrl } = use(DataContext);
  const { connect, disconnect, readyState, registerCommand, sendCommand } = useChannelLayer(socketUrl);

  useEffect(() => {
    if (socketUrl && readyState === 3) {
        console.log("ChannelProvider | Connect socket: ", socketUrl, readyState)
        connect()
    }
  }, [socketUrl]);

  useEffect(() => {
    // On mount
    console.log("ChannelProvider | Init | Mounting component")
    if (socketUrl && readyState === 3) {
        console.log("ChannelProvider | Connect socket: ", socketUrl, readyState)
        connect()
    }

    // On Unmount
    return () => {
        if (socketUrl && readyState !== 3)
        disconnect()
        console.log("ChannelProvider | Unmounting, disconnecting socket", socketUrl, readyState)
    }
  }, []);

  return (
    <ChannelContext.Provider
      value={{
        connect,
        disconnect,
        readyState,
        registerCommand,
        sendCommand,
        socketUrl,
      }}
    >
      {children}
    </ChannelContext.Provider>
  );
};

export default ChannelProvider;