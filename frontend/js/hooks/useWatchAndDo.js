import React, {useEffect} from 'react';



export const useWatchAndDo = (watch, andDo) => {

  useEffect(() => {
    andDo()

  }, [watch]);

}