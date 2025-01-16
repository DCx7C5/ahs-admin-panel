import React, {use, useCallback, useEffect, useState} from 'react';
import BookmarkCategory from "./BookmarkCategory";
import {SocketContext} from "../SocketProvider";
import './css/bookmarks.scss'


const Bookmarks = () => {
  const [categories, setCategories] = useState([])
  const {
    webSocketIns,
    readyState,
    registerMsgCallback,
  } = use(SocketContext)

  useEffect(() => {
    registerMsgCallback('bookmarks', 'get_bm_categories', saveCategory)
    console.log('bookmarks mounted')

    return () => {
      console.log('bookmarks unmounted')
    }
  }, []);


  useEffect(() => {
    if (readyState === 1 && webSocketIns && categories.length === 0) {
      getCategories()
    }
  }, [readyState, webSocketIns, categories])

  const saveCategory = useCallback((data) => {
    console.log('saveCategory', data)
    setCategories((prevState) =>[...prevState, data])
  },[setCategories])


  const getBookmarks = useCallback((uniqueId, id) => {
    webSocketIns.send(JSON.stringify({
      app: "bookmarks",
      func_name: "get_bookmarks",
      func_args: [id],
      unique_call_id: uniqueId,
    }))
  }, [webSocketIns])


  const getCategories = () => {
    webSocketIns.send(JSON.stringify({
      app: "bookmarks",
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