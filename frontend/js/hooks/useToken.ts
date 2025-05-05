import {useCallback, useEffect, useState} from "react";
import {base64UrlDecode, base64UrlEncode} from "../components/utils";
import {cryptoApi} from "./useECCryptography";

export interface AHSToken {
    token: string | null,
    header: {} | null,
    payload: {} | null,
    signature: string | null,
    parseResponseToken: (token: string) => void,
}

export interface TokenPayload {
    expires: number | string | Date,
    username: string,
    isAuthenticated: boolean,
    isSuperuser: boolean,

}


export const useToken = (): AHSToken => {
    const [header, setHeader] = useState<{} | null>(null)
    const [payload, setPayload] = useState<{} | null>(null)
    const [signature, setSignature] = useState<string | null>(null)
    const [token, setToken] = useState<string | null>(null)


    useEffect(() => {
        console.log("useToken ", )
        return () => {
            console.log("useToken cleanup")
            setPayload({})
            setSignature('')
            setHeader({})
        }
    }, []);

    const parseResponseToken = useCallback(async (token: string) => {

    },[])

    return {
        token,
        header,
        payload,
        signature,
        parseResponseToken,
    };
}

export default useToken;