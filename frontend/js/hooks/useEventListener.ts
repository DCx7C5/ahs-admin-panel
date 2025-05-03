import { useEffect, useRef } from "react";

type EventListenerCallback = (event: Event) => void;
type EventListenerElement = Window | Element | null;

interface UseEventListenerOptions {
  eventType: string;
  callback: EventListenerCallback;
  element?: EventListenerElement;
}

/**
 * A hook that attaches an event listener to a specified element
 * @param eventType - The event type to listen for
 * @param callback - The callback function to execute when the event occurs
 * @param element - The DOM element to attach the listener to (defaults to window)
 */
const useEventListener = (
  eventType: string,
  callback: EventListenerCallback,
  element: EventListenerElement = window
): void => {
  const callbackRef = useRef<EventListenerCallback>(callback);

  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  useEffect(() => {
    if (element == null) return;
    const handler = (event: Event) => callbackRef.current(event);
    element.addEventListener(eventType, handler);

    return () => element.removeEventListener(eventType, handler);
  }, [eventType, element]);
};

export default useEventListener;
