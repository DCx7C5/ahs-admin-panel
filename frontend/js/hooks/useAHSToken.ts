import {useCallback, useEffect, useState} from "react";


export const useAHSToken = (cryptoClient) => {
    const [token, setToken] = useState<string>("");
    const [header, setHeader] = useState<{}>({})
    const [payload, setPayload] = useState<{}>({})
    const [signature, setSignature] = useState<string>(null)

    useEffect(() => {
        const h = base64UrlEncode(header)
        const p = base64UrlEncode(payload)
        setSignature(base64UrlEncode(cryptoClient.sign(`${h}.${p}`)))

        console.log("useAHSToken ", signature, h, p)
    }, [header, payload])

    useEffect(() => {
        setToken(`${header}.${payload}.${signature}`)
    }, [signature]);


    const addTokenHeader = useCallback(
        async (headerKey: string, headerValue: any) => {
            setHeader((prevState) => ({
                ...prevState,
                [headerKey]: headerValue,
            }))
    },[])

    const addTokenPayload = useCallback(
        async (payloadKey: string, payloadValue: any) => {
            setHeader((prevState) => ({
                ...prevState,
                [payloadKey]: payloadValue,
            }))
    },[])

    function base64UrlEncode(str) {
        return btoa(str) // Convert to Base64
            .replace(/\+/g, '-') // Replace + with -
            .replace(/\//g, '_') // Replace / with _
            .replace(/=+$/, ''); // Remove padding
    }

    function base64UrlDecode(str) {
        str = str.replace(/-/g, '+').replace(/_/g, '/'); // Convert back to Base64
        while (str.length % 4) {
            str += '='; // Add padding if needed
        }
        return atob(str); // Decode Base64
    }

    return {
        token,
        addTokenHeader,
        addTokenPayload,
    };
}

export default useAHSToken;