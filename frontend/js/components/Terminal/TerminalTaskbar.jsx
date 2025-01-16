import React, {lazy, Suspense, use, useEffect} from "react";
import { TerminalContext } from "./TerminalDataProvider";
import StartResetButton from "./StartResetButton";
import StopButton from "./StopButton";

const TerminalSessionTab = lazy(() =>
  import("./TerminalSessionTab").then((module) => ({
    default: module.TerminalSessionTab,
  }))
);

export const CreateSessionButton = () => {
  const { sessions, createSession } = use(TerminalContext);

  return (
    <button
      id="new-tab-button"
      className="tab-element ctrl-button btn"
      disabled={sessions.length >= 9}
      onClick={() => createSession()}

    >
      <div className="tab-create-button">+</div>
    </button>
  );
};

export const TerminalTaskbar = () => {
  const { sessions } = use(TerminalContext);

  return (
    <div className="term-tabbar">
      <StartResetButton />
      <StopButton />
      <Suspense>
        {sessions.map((session, i) => (
          <TerminalSessionTab
            session={session}
            key={i}
          />
        ))}
      </Suspense>
      <CreateSessionButton />
    </div>
  );
};

export default TerminalTaskbar;