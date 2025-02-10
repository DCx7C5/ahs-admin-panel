import { useEffect, useCallback, useRef } from "react";
import { useSocket } from "./useSocket";

interface RegisterCommandInput {
  command_name: string; // The name of the command to register
  command: string; // The command content
  callback: (data: any) => void; // Callback function to handle the command response
}

interface UseChannelLayerOutput {
  connect: () => void;
  disconnect: () => void;
  readyState: number;
  registerCommand: (input: RegisterCommandInput) => void;
  sendCommand: (command: string, data: any) => void;
}

export const useChannelLayer = (socketUrl: string, options = {}): UseChannelLayerOutput => {
  const {
    manual = false,
  } = options;
  const {
    connect,
    disconnect,
    readyState,
    webSocketIns,
  } = useSocket(socketUrl, {
    reconnectLimit: 10,
    reconnectInterval: 10000,
    manual: manual,
  });

  const commandsRef = useRef<Record<string, (data: any) => void>>({});

  // Establish and clean up WebSocket connection
  useEffect(() => {
    console.log("useChannelLayer | Mounted and connecting to socket");
    connect();

    return () => {
      console.log("useChannelLayer | Unmounted, disconnecting socket");
      disconnect();
    };
  }, [connect, disconnect]);

  // Handle incoming WebSocket messages
  useEffect(() => {
    if (webSocketIns && readyState === WebSocket.OPEN) {
      console.log("useChannelLayer | Socket connection is open");

      // Listen for incoming messages
      const handleMessage = (messageEvent: MessageEvent) => {
        const data = JSON.parse(messageEvent.data);
        const { command, payload } = data;

        console.log("useChannelLayer | Received message:", data);

        // Trigger corresponding registered command callback
        if (commandsRef.current[command]) {
          commandsRef.current[command](payload);
        } else {
          console.warn(`useChannelLayer | No registered callback for command: ${command}`);
        }
      };

      webSocketIns.addEventListener("message", handleMessage);

      return () => {
        webSocketIns.removeEventListener("message", handleMessage);
      };
    }
  }, [webSocketIns, readyState]);

  // Register a command and its callback
  const registerCommand = useCallback(({ command_name, command, callback }: RegisterCommandInput) => {
    if (commandsRef.current[command]) {
      console.warn(`useChannelLayer | Command already registered: ${command}`);
      return;
    }

    console.log("useChannelLayer | Registering command:", command);
    commandsRef.current[command] = callback;

    // Notify server about the registered command (optional)
    if (webSocketIns && webSocketIns.readyState === WebSocket.OPEN) {
      webSocketIns.send(JSON.stringify({ type: "command.register", command_name, command }));
    }
  }, [webSocketIns]);

  // Method to send a command with its payload
  const sendCommand = useCallback(
    (command: string, data: any) => {
      if (webSocketIns && readyState === WebSocket.OPEN) {
        console.log("useChannelLayer | Sending command:", command, data);
        webSocketIns.send(JSON.stringify({ type: "command.execute", command, data }));
      } else {
        console.error("useChannelLayer | WebSocket is not ready to send commands");
      }
    },
    [webSocketIns, readyState]
  );

  return {
    connect,
    disconnect,
    readyState,
    registerCommand,
    sendCommand,
  };
};

export default useChannelLayer;