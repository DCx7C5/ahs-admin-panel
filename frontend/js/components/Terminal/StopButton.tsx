import React from "react";
import { TerminalContext } from "./TerminalDataProvider";

// Type definitions for TerminalContext values
interface TerminalContextType {
  sessions: { id: string }[]; // Assuming sessions is an array of session objects
  closeSession: (sessionId: string) => void;
  getActiveSessionId: () => string;
}

export const StopButton: React.FC = () => {
  const { sessions, closeSession, getActiveSessionId } =
    React.useContext(TerminalContext) as TerminalContextType;

  const handleClick = () => {
    const activeSessionId = getActiveSessionId();
    closeSession(activeSessionId);
  };

  return (
    <button
      id="stop-btn"
      className="tab-element ctrl-button btn"
      disabled={sessions.length === 0}
      onClick={handleClick}
    >
      <i className={"bi bi-stop-fill"}></i>
    </button>
  );
};

export default StopButton;