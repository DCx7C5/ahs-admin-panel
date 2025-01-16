import {useCallback, useEffect, useRef} from "react";
import PropTypes from "prop-types";


export const useTimeout = (cb, delay) => {
  const cbRef = useRef(cb);
  const timeoutRef = useRef(null);

  useEffect(() => {
    cbRef.current = cb
  }, [cb]);

  const set = useCallback(() => {
    timeoutRef.current = setTimeout(() => cbRef.current(), delay)
  }, [delay])

  const clear = useCallback(() => {
    timeoutRef.current && clearTimeout(timeoutRef.current)
  }, [])

  useEffect(() => {
    set()
    return clear
  }, [delay, set, clear]);

  const reset = useCallback(() => {
    clear()
    set()
  }, [clear, set])

  return [reset, clear]
}

useTimeout.propTypes = {
  cb: PropTypes.func.isRequired,
  delay: PropTypes.number.isRequired,
};

export default useTimeout