import { useEffect, useRef, useState } from "react";
import PropTypes from "prop-types";
import { useLocalStorage } from "./useStorage";

const useMoveElement = (elementRef, minX = 0, minY = 0) => {
  const [position, setPosition] = useState([0, 0]);
  const isDownRef = useRef(false);
  const isDraggingRef = useRef(false);
  const deltaRef = useRef([0, 0]);
  const frameId = useRef(0);
  const [positionStorage, setPositionStorage] = useLocalStorage(
    'posStorage', [null, null]);

  useEffect(() => {
    if (elementRef.current) {
      elementRef.current.style.position = "absolute";

      const parent = elementRef.current.parentElement;

      const maxX = parent.clientWidth - elementRef.current.clientWidth;
      const maxY = parent.clientHeight - elementRef.current.clientHeight;

      (positionStorage[0] !== null && positionStorage[1] !== null)
        ? setPosition([
            Math.min(positionStorage[0], maxX),
            Math.min(positionStorage[1], maxY),
          ])
        : setPosition([elementRef.current.offsetLeft, elementRef.current.offsetTop]);
    }

    console.log(elementRef.current.offsetLeft, elementRef.current.offsetTop);

    return () => cancelAnimationFrame(frameId.current);
  }, []);

  const clamp = (value, min, max) => Math.max(min, Math.min(value, max));

  const animate = () => {
    if (isDownRef.current && isDraggingRef.current) {
      const parent = elementRef.current.parentElement;

      const maxX = parent.clientWidth - elementRef.current.clientWidth;
      const maxY = parent.clientHeight - elementRef.current.clientHeight;

      const newLeft = clamp(position[0] + deltaRef.current[0], 0, maxX);
      const newTop = clamp(position[1] + deltaRef.current[1], 0, maxY);

      setPosition([newLeft, newTop]);

      frameId.current = requestAnimationFrame(animate);
    }
  };

  const handleMouseDown = e => {
    e.preventDefault();
    isDownRef.current = true;
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
  };

  const handleMouseMove = e => {
    e.preventDefault();
    if (!isDownRef.current) return;
    isDraggingRef.current = true;
    deltaRef.current = [deltaRef.current[0] + e.movementX, deltaRef.current[1] + e.movementY];
    frameId.current = requestAnimationFrame(animate);
  };

  const handleMouseUp = e => {
    e.preventDefault();
    isDownRef.current = false;
    isDraggingRef.current = false
    cancelAnimationFrame(frameId.current)
    setPositionStorage([elementRef.current.offsetLeft, elementRef.current.offsetTop]);
    console.log(positionStorage)
    deltaRef.current = [0, 0];
    window.removeEventListener('mousemove', handleMouseMove);
    window.removeEventListener('mouseup', handleMouseUp);
  };

  return [position, handleMouseDown];
};

useMoveElement.propTypes = {
  elementRef: PropTypes.oneOfType([
    PropTypes.shape({ current: PropTypes.instanceOf(Element) }),
  ]).isRequired,
};

export default useMoveElement;
