import React, {use, useCallback, useEffect, useRef, useState} from "react";
import useDraggable from "../../hooks/useDraggable";
import PropTypes from "prop-types";
import {SocketContext} from "../SocketProvider";




export const BookmarkCategory = ({categoryData, getBookmarks}) => {
  const elementRef = useRef(null);
  const [dx, dy, handleMouseDown, isDragging] = useDraggable({
    elementRef,
    gridSize: 1,
    uniqueId: categoryData.uuid,
  });
  const { webSocketIns, readyState, registerMsgCallback } = use(SocketContext);
  const [bookmarks, setBookmarks] = useState([]);
  const { name, uuid, id, active } = categoryData;

  const handleMsgCallback = useCallback((data) => {
    setBookmarks((prevState) => [...prevState, data])
  },[setBookmarks])

  useEffect(() => {
    registerMsgCallback('bookmarks', 'get_bookmarks', handleMsgCallback, {id: id}, uuid)
  }, []);

  /*useEffect(() => {
    if (!categoryData) return;
    if (webSocketIns && readyState === 1 && bookmarks.length === 0 && id && uuid) {
      console.log('WebSocket is open, fetching bookmarks for category:', id);
      getBookmarks(id);
    }
  }, [readyState, webSocketIns, id, uuid, bookmarks, getBookmarks]);
*/
  return (
    <div
      ref={elementRef}
      className="bm-cat col"
      onMouseDown={handleMouseDown}
      style={{transform: `translate3d(${dx}px, ${dy}px, 0)`, cursor: isDragging ? 'grabbing' : null}}
    >
      <h5 className={"bm-cat-title"}>{name}</h5>
      <div className={"bm-cat-content"}>
        {/* Render bookmarks */}

      </div>
    </div>
  );
};

BookmarkCategory.propTypes = {
  categoryData: PropTypes.shape({
    name: PropTypes.string,
    uuid: PropTypes.string,
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  }).isRequired,
};
export default BookmarkCategory;