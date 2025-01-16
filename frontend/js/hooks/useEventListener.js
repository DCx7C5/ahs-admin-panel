import {useEffect, useRef} from "react";
import PropTypes from "prop-types";


const useEventListener = (eventType, callback, element = window) => {
  const callbackRef = useRef(callback);

  useEffect(() => {
    callbackRef.current = callback
  }, [callback]);

  useEffect(() => {
    if (element == null) return
    const handler = event => callbackRef.current(event)
    element.addEventListener(eventType, handler)

    return () => element.removeEventListener(eventType, handler)
  }, [eventType, element]);
}

useEventListener.propTypes = {
  eventType: PropTypes.string.isRequired,
  callback: PropTypes.func.isRequired,
  element: PropTypes.oneOfType([
    PropTypes.instanceOf(Element),
    PropTypes.instanceOf(Window),
  ]),
};

export default useEventListener