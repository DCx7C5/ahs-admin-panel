import {useCallback, useEffect, useState} from "react";
import {base64UrlDecode, base64UrlEncode} from "../components/utils";


export const useAHSToken = (cryptoClient) => {
    const [token, setToken] = useState<string>("");
    const [isBuilding, setIsBuilding] = useState<boolean>(false);
    const [payload, setPayload] = useState<{}>({})

    useEffect(() => {
        console.log("useAHSToken ", )

        return () => {
            console.log("useAHSToken cleanup")
            setPayload({})
            setToken('')
        }
    }, []);

    // if payload changes it creates a new header and signature
    useEffect(() => {
        if (isBuilding) return
        const h = createTokenHeader()
        const p = base64UrlEncode(payload)
        const s: string = createTokenSignature(h, p)
        setToken(`${h}.${p}.${s}`)
        console.log("useAHSToken ", token, base64UrlDecode(h), base64UrlDecode(p))
    }, [payload])

    const createTokenHeader = () => {
        return base64UrlEncode({
            date: new Date().toISOString(),
        })
    }

    const createTokenSignature = (h, p) => {
      return base64UrlEncode(cryptoClient.sign(`${h}.${p}`))
    }

    const addTokenPayload = useCallback(
        async (payloadKey: string, payloadValue: any) => {
            setPayload((prevState) => ({
                ...prevState,
                [payloadKey]: payloadValue,
            }))
    },[])


    return {
        token,
        addTokenPayload,
    };
}

export default useAHSToken;