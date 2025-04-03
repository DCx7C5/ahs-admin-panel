import { useState, useEffect } from "react";

const useClientWidth = (ref) => {
  const [clientWidth, setClientWidth] = useState(100);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    const updateWidth = () => {
      setClientWidth(element.clientWidth); // Dynamically update the width
    };

    // Initialize `ResizeObserver` to track the element's size
    const resizeObserver = new ResizeObserver(updateWidth);
    resizeObserver.observe(element); // Start observing the referenced element

    // Set initial width immediately
    updateWidth();


    return () => {
      resizeObserver.disconnect();
    };
  }, []);

  if (clientWidth === 100) {
    return `${clientWidth}%`;
  } else {
    return `${clientWidth}px`;
  }

}

export default useClientWidth;