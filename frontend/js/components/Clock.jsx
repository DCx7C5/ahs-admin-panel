import React, {useEffect} from "react";

export const RealTimeClock = () => {
  const [date, setDate] = React.useState(new Date());

  useEffect(() => {
    const timerID = setInterval(() => tick(), 1000);
    return () => {
      clearInterval(timerID);
    };
  });
  function tick() {
    setDate(new Date());
  }

  return <div className="rtclock ">{date.toLocaleTimeString()}</div>
}

export default RealTimeClock