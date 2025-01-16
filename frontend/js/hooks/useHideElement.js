import {useEffect, useState} from "react";
import {useLocalStorage} from "./useStorage";
import PropTypes from "prop-types";


export const useHideElement = (initialValue = false, storageKey = null, elementRef = null) => {
  const [isVisible, setIsVisible, _] = (typeof storageKey === 'string')
    ? useLocalStorage(storageKey, initialValue)
    : useState(initialValue)

  useEffect(() => {
    if (elementRef && isVisible && !elementRef.current.classList.contains('visible'))
      show()
  }, []);

  const hide = () => {
    setIsVisible(false)
    if (elementRef && elementRef.current) elementRef.current.classList.remove('visible')
  }

  const show = () => {
    setIsVisible(true)
    if (elementRef && elementRef.current) elementRef.current.classList.add('visible')
  }

  const toggle = () => {
    setIsVisible((prev) => !prev)
    if (elementRef && elementRef.current) elementRef.current.classList.toggle('visible')
  }

  return [
    isVisible,
    hide,
    show,
    toggle
  ]
}

useHideElement.propTypes = {
  initialValue: PropTypes.bool.isRequired,
  storageKey: PropTypes.string
}


export default useHideElement