import React, {use, useCallback, useEffect, useRef, useState} from 'react';
import BookmarkCategory from "./BookmarkCategory";
import './css/bookmarks.scss'
import useAHSCommand from "../../hooks/useAHSCommand";
import {SocketContext} from "../SocketProvider";
import {ChannelContext} from "../ChannelProvider";



const Bookmarks = () => {
  const { webSocketIns, readyState} = use(ChannelContext)
  const requestDone = useRef(false)
  const [categories, setCategories] = useState([])


  useEffect(() => {
    console.log('bookmarks mounted')

    return () => {
      console.log('bookmarks unmounted')
    }
  }, []);

  useEffect(() => {
    if (!requestDone.current && readyState === 1 && webSocketIns) {
      getCategories()
      requestDone.current = true
      console.log('WebSocket is open, fetching categories')
    }
  }, [readyState, webSocketIns, categories, requestDone])

  const saveCategory = useCallback((data) => {
    console.log('saveCategory', data)
    setCategories((prevState) =>[...prevState, data])
  },[setCategories])

  const getBookmarks = useCallback((uniqueId, id) => {
    webSocketIns.send(JSON.stringify({
      type: "command.request",
      func_name: "get_bookmarks",
      func_args: [id, uniqueId],
      unique_id: uniqueId,
    }))
  }, [webSocketIns])

  const getCategories = () => {
    webSocketIns.send(JSON.stringify({
      type: "command.request",
      func_name: "get_bm_categories",
    }))
  }

  return (
    <div className="bookmarks">
      {categories &&
        categories.map((cat, i) => (
          <BookmarkCategory key={cat.id}
                            categoryData={cat}
                            getBookmarks={getBookmarks}
          />
        ))
      }
    </div>
  )
}


export default Bookmarks;