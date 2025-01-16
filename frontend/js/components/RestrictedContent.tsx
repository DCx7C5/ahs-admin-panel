import React, {use} from "react";
import {DataContext} from "./DataProvider";


interface RestrictedContentProps {
  children: React.ReactNode;
}

export const RestrictedContent: React.FC<RestrictedContentProps> = (
    {children}
) => {
  const {user}  = use(DataContext);
  const {is_superuser} = user;
  return (
    <>
        {is_superuser && children}
    </>
  )
}

export default RestrictedContent;