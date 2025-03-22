import {useCallback, useEffect, useRef, useState} from "react";
import argon2id from 'argon2-browser';
import {IndexedDB} from "./useIndexedDB";
import {ab2hex, base64UrlEncode, hex2ab, str2ab} from "../components/utils";

const curve = 'P-521'
const orderHex = '01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409'
const prefixHex = '3060020100301006072a8648ce3d020106052b81040023044930470201010442'




interface Cryptography {
    encrypt: (data: (ArrayBuffer | ArrayBufferView)) => Promise<string>,
    decrypt: (encryptedPayload: string) => Promise<string>,
    sign: (data: (ArrayBuffer | ArrayBufferView)) => Promise<Uint8Array>,
    verify: (data: (ArrayBuffer | ArrayBufferView), signature: ArrayBuffer) => Promise<boolean>,
    deriveSharedSecret: (privateKey: any, foreignPublicKey: any) => Promise<ArrayBuffer>,
    getPublicFromPrivate: (privateKeyCK: any) => Promise<CryptoKey>,
    deriveRawPrivateArgon: (saltAB: string, passphraseCK: any) => Promise<Uint8Array>,
    deriveRawPrivate: (saltAB: string, passphraseCK: any) => Promise<Uint8Array>,
    generateKeyFromPassword: (password: string, salt: string, type?: ("argon" | "pbkdf2")) => Promise<{privateKeyCK: CryptoKey, pkcs8AB: ArrayBuffer}>,
    generateRandomSalt: () => string,
    keysGenerated: boolean,
}

export const useCryptography = (indexedDB: IndexedDB):Cryptography => {
    const [keysGenerated, setKeysGenerated] = useState(false);
    const {size, kdfHash, kdfIterations} = useRef({
        size: hex2ab(orderHex).byteLength * 8,
        kdfHash: 'SHA-256',
        kdfIterations: 100000,
    }).current

    useEffect(() => {

    }, []);

    const sign = useCallback(async (data: ArrayBuffer | ArrayBufferView) => {
        try {
            const privateKeyData = await indexedDB.getPrivateKey();
            if (!privateKeyData) {
                throw new Error("Private key not found")
            }

            const privateKey = await crypto.subtle.importKey(
                'pkcs8',
                str2ab(privateKeyData),
                { name: 'ECDSA', namedCurve: curve },
                false,
                ['sign']
            );


            const signature = await crypto.subtle.sign(
                { name: 'ECDSA', hash: { name: kdfHash } },
                privateKey,
                data
            );

            return base64UrlEncode(new Uint8Array(signature)); // Return signature as Uint8Array
        } catch (error) {
            console.error("Error signing data:", error);
            throw error;
        }
    }, [indexedDB]);

    const verify = useCallback(async (data: ArrayBuffer | ArrayBufferView, signature: ArrayBuffer) => {
        try {
            const publicKeyData = await indexedDB.getPublicKey();
            if (!publicKeyData) throw new Error("Public key not found");

            const publicKey = await crypto.subtle.importKey(
                'spki',
                str2ab(publicKeyData),
                { name: 'ECDSA', namedCurve: curve },
                false,
                ['verify']
            );

        return await crypto.subtle.verify(
                {name: 'ECDSA', hash: {name: kdfHash}},
                publicKey,
                signature,
                data
            ); // Boolean indicating if signature is valid
        } catch (error) {
            console.error("Error verifying signature:", error);
            throw error;
        }
    }, [indexedDB]);


    const encrypt = useCallback(async (data: ArrayBuffer | ArrayBufferView) => {
        try {
            const privateKeyData = await indexedDB.getPrivateKey();
            const serverPublicKeyData = await indexedDB.getServerPublicKey();

            if (!privateKeyData || !serverPublicKeyData) {
                throw new Error("Keys are missing for encryption");
            }

            const privateKey = await crypto.subtle.importKey(
                'pkcs8',
                str2ab(privateKeyData),
                { name: 'ECDH', namedCurve: curve },
                false,
                ['deriveBits']
            );

            const foreignPublicKey = await crypto.subtle.importKey(
                'spki',
                str2ab(serverPublicKeyData),
                { name: 'ECDH', namedCurve: curve },
                false,
                []
            );

            const sharedSecret = await crypto.subtle.deriveBits(
                { name: 'ECDH', public: foreignPublicKey },
                privateKey,
                size
            );

            const aesKey = await crypto.subtle.importKey(
                'raw',
                sharedSecret,
                { name: 'AES-GCM' },
                false,
                ['encrypt']
            );

            const iv = crypto.getRandomValues(new Uint8Array(12)); // Initialization vector
            const encryptedData = await crypto.subtle.encrypt(
                { name: 'AES-GCM', iv },
                aesKey,
                data
            );

            return JSON.stringify({
                iv: ab2hex(iv),
                ciphertext: ab2hex(new Uint8Array(encryptedData)),
            });
        } catch (error) {
            console.error("Error encrypting data:", error);
            throw error;
        }
    }, [indexedDB]);


    const decrypt = useCallback(async (encryptedPayload: string) => {
        try {
            const privateKeyData = await indexedDB.getPrivateKey();
            const serverPublicKeyData = await indexedDB.getServerPublicKey();

            if (!privateKeyData || !serverPublicKeyData) {
                throw new Error("Keys are missing for decryption");
            }

            const privateKey = await crypto.subtle.importKey(
                'pkcs8',
                str2ab(privateKeyData),
                { name: 'ECDH', namedCurve: curve },
                false,
                ['deriveBits']
            );

            const foreignPublicKey = await crypto.subtle.importKey(
                'spki',
                str2ab(serverPublicKeyData),
                { name: 'ECDH', namedCurve: curve },
                false,
                []
            );

            const sharedSecret = await crypto.subtle.deriveBits(
                { name: 'ECDH', public: foreignPublicKey },
                privateKey,
                size
            );

            const aesKey = await crypto.subtle.importKey(
                'raw',
                sharedSecret,
                { name: 'AES-GCM' },
                false,
                ['decrypt']
            );

            const payload = JSON.parse(encryptedPayload);
            const iv = hex2ab(payload.iv);
            const ciphertext = hex2ab(payload.ciphertext);

            const decryptedData = await crypto.subtle.decrypt(
                { name: 'AES-GCM', iv },
                aesKey,
                ciphertext
            );

            return new TextDecoder().decode(decryptedData); // Convert decrypted data to string
        } catch (error) {
            console.error("Error decrypting data:", error);
            throw error;
        }
    }, [indexedDB]);

    const generateRandomSalt = useCallback(
        () => {
            const random = crypto.getRandomValues(new Uint8Array(48));
            return base64UrlEncode(String.fromCharCode(...random))
    }, [])

    async function generateKeyFromPassword(password: string, salt: string, type: "argon" | "pbkdf2" = "pbkdf2") {
        const textEncoder = new TextEncoder();
        const deriveFunc = type === "pbkdf2"
            ? deriveRawPrivate
            : deriveRawPrivateArgon;
        try {
            console.log("passphraseAB", password);
            const saltAB = textEncoder.encode(salt);
            const passphraseCK = await crypto.subtle.importKey('raw', textEncoder.encode(password), { name: 'PBKDF2' }, false, ['deriveBits']);
            const rawPrivateEcKeyAB = await deriveFunc(saltAB, passphraseCK);
            const pkcs8nopubAB = new Uint8Array([ ...hex2ab(prefixHex), ...new Uint8Array(rawPrivateEcKeyAB)])
            const algo = { name: 'ECDSA', namedCurve: curve }
            const privateKeyCK = await crypto.subtle.importKey('pkcs8', pkcs8nopubAB, algo, true, ['sign'] )
            const pkcs8AB = await crypto.subtle.exportKey('pkcs8', privateKeyCK)
            await indexedDB.storePrivateKey(privateKeyCK, pkcs8AB)
            return {privateKeyCK, pkcs8AB}

        } catch (error) {
            console.error("Error generating key from password:", error);
            throw error; // Ensure no retries or loops happen implicitly
        }
    }


    async function deriveRawPrivate(salt: ArrayBuffer, passphrase: CryptoKey){
        console.log("deriveRawPrivate", salt, passphrase);
        const algo = { name: 'PBKDF2', salt: salt, iterations: kdfIterations, hash: kdfHash }
        const rawKeyAB = await crypto.subtle.deriveBits(algo, passphrase, size)
           const nBI = BigInt('0x' + orderHex);
           let rawKeyBI = BigInt('0x' + ab2hex(rawKeyAB));
           console.log("Initial rawKeyBI:", rawKeyBI); // Debugging step

           if (rawKeyBI >= nBI) {
               rawKeyBI = rawKeyBI % nBI;
               console.log("Adjusted rawKeyBI:", rawKeyBI); // Ensure this doesn't keep happening
           }

           if (rawKeyBI < BigInt(0)) {
               throw new Error("Derived key is invalid: less than 0"); // Make issues visible
           }
        const rawKeyHex = rawKeyBI.toString(16).padStart(2*(size/8), '0') // if shorter, pad with 0x00 to fixed size
        return hex2ab(rawKeyHex)
    }

    async function deriveRawPrivateArgon(saltAB: ArrayBuffer, passphraseCK: CryptoKey) {
        const textEncoder = new TextEncoder();

        return (await argon2id.hash({
            pass: new Uint8Array(saltAB),
            salt: base64UrlEncode(passphraseCK),
            time: 1,
            mem: 65536,
            parallelism: 1,
            hashLen: 528
        })).hash;
    }

    async function deriveSharedSecret(privateKey: CryptoKey, foreignPublicKey: CryptoKey): Promise<ArrayBuffer> {
        return await crypto.subtle.deriveBits(
            {
                name: "ECDH",
                public: foreignPublicKey,
            },
            privateKey,
            521
        );
    }

    async function getPublicFromPrivate(privateKeyCK: CryptoKey){
        const publicKey = await crypto.subtle.exportKey('spki', privateKeyCK)

        const algo = { name: 'ECDH', namedCurve: curve }
        return
    }

    return {
        encrypt,
        decrypt,
        sign,
        verify,
        deriveSharedSecret,
        getPublicFromPrivate,
        deriveRawPrivateArgon,
        deriveRawPrivate,
        generateKeyFromPassword,
        generateRandomSalt,
        keysGenerated,
    };
}

export default useCryptography;