import {useEffect, useRef, useState} from "react";
import useEventListener from "./useEventListener";
import PropTypes from "prop-types";
import {useLocalStorage} from "./useStorage";


const useMoveElementVertical = (ref, direction = 'both', handleClick = null, minTop = 0) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isDown, setIsDown] = useState(false);
  const [positionTopinStorage, setPositionTopinStorage, _] = useLocalStorage(
    'term.btn.pos', window.innerHeight / 2
  );
  const [topDistance, setTopDistance] = useState(positionTopinStorage);
  const coords = useRef({
    lastTop: 0,
    mouseStartY: 0,
    distanceTop: 0,
  });


  useEffect(() => {
    coords.current.lastTop = positionTopinStorage
    setTopDistance(positionTopinStorage)
  }, []);

  const handleMouseMove = e => {
    e.preventDefault();
    if (isDown && ref.current) {
      setIsDragging(true);
      const deltaY = e.pageY - coords.current.mouseStartY;

      let ntopDistance = coords.current.distanceTop + deltaY;

      const mintoTop = minTop;
      const maxtoTop = window.innerHeight - ref.current.offsetHeight;
      coords.current.lastTop = ntopDistance = Math.max(mintoTop, Math.min(ntopDistance, maxtoTop));

      setTopDistance(ntopDistance);
    }
  }

  useEventListener('mousemove', handleMouseMove)

  const onMouseClick = () => {
    if (!isDragging && handleClick) handleClick()
  }

  const onMouseDown = e => {
    setIsDown(true);
    e.preventDefault();
    coords.current.mouseStartY = e.pageY;
    coords.current.distanceTop = ref.current.offsetTop;
    window.addEventListener('mouseup', handleMouseUp)
  }

  const handleMouseUp = e => {
    e.preventDefault()
    setTimeout(setIsDragging, 100, false)
    setIsDown(false)
    coords.current.lastTop !== 0 && setPositionTopinStorage(coords.current.lastTop)
    window.removeEventListener('mouseup', handleMouseUp)
  }

  return [topDistance, onMouseDown , onMouseClick]
}

useMoveElementVertical.propTypes = {
  ref: PropTypes.oneOfType([
    PropTypes.shape({ current: PropTypes.instanceOf(Element) }),
    PropTypes.instanceOf(Element),
    PropTypes.object,
  ]).isRequired,
  direction: PropTypes.string,
  onclick: PropTypes.func,
}


export default useMoveElementVertical