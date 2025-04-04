import React from "react";
import { TerminalContext } from "./TerminalDataProvider";

// Type definitions for TerminalContext values
interface TerminalContextType {
  closeSession: (sessionId: string) => void;
  createSession: () => void;
  activeSessionId: string;
  sessions: { id: string }[]; // Assuming sessions is an array of session objects
}

export const StartResetButton: React.FC = () => {
  const { closeSession, createSession, activeSessionId, sessions } =
    React.useContext(TerminalContext) as TerminalContextType;

  const handleClick = () => {
    if (sessions.length > 0) {
      closeSession(activeSessionId);
      createSession();
    } else {
      createSession();
    }
  };

  return (
    <button
      id="start-btn"
      className="tab-element ctrl-button btn"
      onClick={handleClick}
    >
      <i
        className={`bi ${
          sessions.length !== 0 ? "bi-arrow-repeat" : "bi-play-fill"
        }`}
        style={{ fontWeight: "bold" }}
      ></i>
    </button>
  );
};

export default StartResetButton;