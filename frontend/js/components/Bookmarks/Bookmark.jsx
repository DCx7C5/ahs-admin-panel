import React, {use} from "react";
import {useDraggable} from "../../hooks/useDraggable";
import useList from "../../hooks/useList";
import './css/bookmarks.scss'
import {SocketContext} from "../SocketProvider";


export const Bookmark = ({parentRef, id, name, url, icon_url}) => {
  const { sendMessage } = use(SocketContext);


  const bmCatList = useList([])
  
  return (
    <div ref={elementRef} className={"bookmark"}>
      <a href={url}>
        <img src={icon_url} alt={`icon_${name}`}/>
      </a>
      <a href={url}>
        {name}
      </a>
    </div>
  )
}

export default Bookmark;