import React, {use, useEffect, useState} from "react";
import {DataContext} from "./DataProvider";


interface RestrictedContentProps {
  children: React.ReactNode;
}


export const RestrictedContent: React.FC<RestrictedContentProps> = ({children}) => {
  const { user, pages } = use(DataContext);
  const {is_superuser} = user;
  const [isAuthenticated, setIsAuthenticated] = useState(true);
  const [hasPermissions, setHasPermissions] = useState(true);

  useEffect(() => {
    console.log("RestrictedContent | Init | Mounted component", user);

    return () => {
      console.log("RestrictedContent | Unmounted component", user);
    }
  }, []);

  useEffect(() => {
    if (!user || !pages) return;
    console.log()


  }, [user, pages]);




  return (
    <>
        {
          isAuthenticated &&
          hasPermissions &&
          is_superuser &&
          children
        }
    </>
  )
}

export default RestrictedContent;
