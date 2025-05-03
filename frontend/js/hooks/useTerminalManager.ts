import { useCallback, useEffect, useRef, useState, RefObject, Dispatch, SetStateAction } from "react";
import { Terminal, ITerminalOptions } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { WebglAddon } from "@xterm/addon-webgl";
import { SerializeAddon } from "@xterm/addon-serialize";
import { Unicode11Addon } from "@xterm/addon-unicode11";
import { AttachAddon } from "@xterm/addon-attach";

/**
 * Interface for a WebSocket connection
 */
interface WebSocketConnection extends WebSocket {
  send: (data: string) => void;
}

/**
 * Interface for a terminal session
 */
interface TerminalSession {
  id: number;
  name: string;
  xterm: Terminal;
  fitAddon: FitAddon;
  webglAddon: WebglAddon;
  serializeAddon: SerializeAddon;
  unicode11Addon: Unicode11Addon;
  webSocketIns: WebSocketConnection | null;
  attachAddon: AttachAddon | null;
  state: string | null;
  active?: boolean;
  close: () => void;
}

/**
 * Props for the useTerminalManager hook
 */
interface UseTerminalManagerProps {
  maxSessions?: number;
  webSocketIns: WebSocketConnection | null;
  connect: () => void;
  disconnect: () => void;
  contentRef: RefObject<HTMLElement>;
}

/**
 * Return type for the useTerminalManager hook
 */
interface UseTerminalManagerReturn {
  sessions: TerminalSession[];
  setSessions: Dispatch<SetStateAction<TerminalSession[]>>;
  createSession: () => TerminalSession | null;
  changeToSession: (toSession: TerminalSession | number, fromSession?: TerminalSession | null) => void;
  handleResize: () => void;
  closeSession: (sessionId: number) => void;
  closeAllSessions: () => void;
  getActiveSession: () => TerminalSession | undefined;
  getActiveSessionId: () => number;
  getSessionById: (id: number) => TerminalSession | undefined;
}

/**
 * Custom hook to manage terminal sessions.
 */
export const useTerminalManager = ({
  maxSessions = 10,
  webSocketIns,
  connect,
  disconnect,
  contentRef,
}: UseTerminalManagerProps): UseTerminalManagerReturn => {
  const [sessions, setSessions] = useState<TerminalSession[]>([]); // Holds all terminal sessions.
  const maxSessionLimit = useRef(maxSessions);
  const [count, setCount] = useState<number>(0);

  useEffect(() => {
    console.log('useTerminalManager', sessions.length);
  }, [sessions]);

  const getActiveSession = useCallback((): TerminalSession | undefined => {
    const s = sessions.find((session) => session.active); // Return the active session object or undefined if none is active
    return s;
  }, [sessions]);

  const getActiveSessionId = useCallback((): number => {
    const activeSession = sessions.find((session) => session.active);
    // Return the activeSession's id (or -1 if there's no active session)
    return activeSession ? activeSession.id : -1;
  }, [sessions]);

  const getSessionById = useCallback(
    (id: number): TerminalSession | undefined => sessions.find((session) => session.id === id),
    [sessions]
  );

  const handleResize = useCallback((): void => {
    const activeSession = getActiveSession();
    if (activeSession && activeSession.xterm && webSocketIns) {
      activeSession.fitAddon.fit();
      webSocketIns.send(JSON.stringify(
        {
          type: 'resize',
          rows: activeSession.xterm.rows,
          cols: activeSession.xterm.cols
        }
      ));
    }
  }, [webSocketIns, getActiveSession]);

  const attachToWebSocket = useCallback((session: TerminalSession): void => {
    if (session.webSocketIns && webSocketIns) {
      const attachAddon = new AttachAddon(session.webSocketIns);
      session.xterm.loadAddon(attachAddon);
      session.webSocketIns = webSocketIns;
    }
  }, [webSocketIns]);

  /**
   * Create a new session.
   */
  const createSession = useCallback((): TerminalSession | null => {
    // Check if we're exceeding the max session limit.
    if (sessions.length >= maxSessionLimit.current) {
      console.warn("Max session limit reached. Cannot create a new session.");
      return null;
    }
    
    connect();
    
    // Initialize a new Terminal instance with add-ons.
    const xtermOptions: ITerminalOptions = {
      cursorBlink: true,
      convertEol: true,
      fontFamily: "JetBrains Mono",
      allowProposedApi: true,
    };
    
    const xterm = new Terminal(xtermOptions);
    const fitAddon = new FitAddon();
    const webglAddon = new WebglAddon();
    const serializeAddon = new SerializeAddon();
    const unicode11Addon = new Unicode11Addon();

    xterm.loadAddon(fitAddon);
    xterm.loadAddon(webglAddon);
    xterm.loadAddon(serializeAddon);
    xterm.loadAddon(unicode11Addon);

    // Create a new TerminalSession instance.
    const session: TerminalSession = {
      id: count,
      name: sessions.length === 0 ? `/bin/zsh` : `/bin/zsh (${sessions.length})`,
      xterm: xterm,
      fitAddon: fitAddon,
      webglAddon: webglAddon,
      serializeAddon: serializeAddon,
      unicode11Addon: unicode11Addon,
      webSocketIns: webSocketIns,
      attachAddon: null,
      state: null,
      close: () => {
        session.xterm.clear();
        session.xterm.dispose();
      },
    };

    setCount(count + 1);
    
    if (contentRef.current) {
      session.xterm.open(contentRef.current);
    }

    if (session.state) {
      session.xterm.write(session.state);
    }

    // Attach WebSocket to the terminal if provided.
    if (webSocketIns && !session.attachAddon) {
      attachToWebSocket(session);
    }

    setSessions((prevSessions) => [...prevSessions, session]);
    console.log(`Session "${session.name}" created.`);

    // Automatically set the newly created session as active.
    setSessions((prevSessions) =>
      prevSessions.map((s) => ({
        ...s,
        active: s.id === session.id, // Set the active session
      }))
    );
    
    return session;
  }, [sessions.length, connect, count, webSocketIns, contentRef, attachToWebSocket]);

  const changeToSession = useCallback((
    toSession: TerminalSession | number, 
    fromSession: TerminalSession | null = null
  ): void => {
    const session = typeof toSession === "object"
      ? toSession
      : getSessionById(toSession);

    if (!session) {
      console.warn("Session does not exist.");
      return;
    }

    if (fromSession) {
      fromSession.state = fromSession.serializeAddon.serialize();
      fromSession.xterm.clear();
      fromSession.xterm.dispose();
    }

    setSessions((prevSessions) =>
      prevSessions.map((s) => ({
        ...s,
        active: s.id === session.id, // Set only the matching session as active
      }))
    );

    if (typeof toSession === "object" && toSession.state) {
      session.xterm.write(toSession.state);
    }

    console.log(`Switched to session: ${session.name}`);
  }, [getSessionById]);

  const closeSession = useCallback((sessionId: number): void => {
    const session = getSessionById(sessionId);

    if (!session) {
      console.warn(`Session with ID ${sessionId} does not exist.`);
      return;
    }

    setSessions((prevSessions) =>
      prevSessions.filter((s) => s.id !== session.id) // Compare by ID
    );
    
    // This seems redundant since we just removed the session
    // But keeping it for compatibility
    setSessions((prevSessions) =>
      prevSessions.map((s) => ({
        ...s,
        active: s.id === session.id, // Set only the matching session as active
      }))
    );
    
    session.close();
  }, [getSessionById]);

  const closeAllSessions = useCallback((): void => {
    sessions.forEach((session) => session.xterm.dispose());
    setSessions([]);
    console.log("All sessions closed.");
  }, [sessions]);

  return {
    sessions,
    setSessions,
    createSession,
    changeToSession,
    handleResize,
    closeSession,
    closeAllSessions,
    getActiveSession,
    getActiveSessionId,
    getSessionById,
  };
};
