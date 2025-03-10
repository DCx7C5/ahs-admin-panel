import {useCallback, useEffect, useRef, useState} from "react";
import argon2id from 'argon2-browser';

const curve = 'P-521'
const orderHex = '01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffa51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409'
const prefixHex = '3060020100301006072a8648ce3d020106052b81040023044930470201010442'

function ab2hex(ab) {
    return Array.prototype.map.call(new Uint8Array(ab), x => ('00' + x.toString(16)).slice(-2)).join('');
}

function hex2ab(hex){
    return new Uint8Array(hex.match(/[\da-f]{2}/gi).map(function (h) { return parseInt(h, 16) }));
}

function str2ab(str) {
  const buf = new ArrayBuffer(str.length);
  const bufView = new Uint8Array(buf);
  for (let i = 0, strLen = str.length; i < strLen; i++) {
    bufView[i] = str.charCodeAt(i);
  }
  return buf;
}


interface Cryptography {
    generatePairFromPassword: any;
    sign:  (data: ArrayBufferView | ArrayBuffer) => Promise<ArrayBuffer>;
    verify:  (data: ArrayBufferView | ArrayBuffer) => Promise<boolean>;
    encrypt:  (data: ArrayBufferView | ArrayBuffer) => Promise<string>;
    decrypt:  () => Promise<string>;
    generateRandomSalt:  () => Promise<Uint8Array>;
    deriveSharedSecret: (privateKey: CryptoKey, foreignPublicKey: CryptoKey) => Promise<ArrayBuffer>;
}

export const useCryptography = (indexedDbClient) => {
    const {size, kdfHash, kdfIterations} = useRef({
        size: hex2ab(orderHex).byteLength * 8,
        kdfHash: 'SHA-512',
        kdfIterations: 100000,
    }).current

    useEffect(() => {

    }, []);

    const sign = useCallback(async (data) => {
        const pubKey = crypto.subtle.exportKey();
        const algo = { name: 'ECDH', namedCurve: curve }
        return crypto.subtle.sign(algo, pubKey, data)
    }, [])

    const verify = useCallback(async (data) => {
        const algo = null
        return crypto.subtle.verify(algo, )
    }, [])

    const encrypt = useCallback(async (data) => {

    }, [])
    const decrypt = useCallback(async () => {

    }, [])

    const generateRandomSalt = useCallback(
        async () => {
            return crypto.getRandomValues(new Uint8Array(32));
    }, [])

    const generateKeyFromPassword = useCallback(
        async (password: string, salt: string, type: "argon" | "pbkdf2" = "pbkdf2")=> {
            console.log("generatePairFromPasswordArgon", password, salt);
            const deriveRawPrivateFunc = type === "pbkdf2"
                ? deriveRawPrivate
                : deriveRawPrivateArgon;
            const textEncoder = new TextEncoder()
            const passphraseAB = textEncoder.encode(password)
            const saltAB = textEncoder.encode(salt)
            // derive raw private key via PBKDF2
            const passphraseCK = await crypto.subtle.importKey('raw', passphraseAB, { name: 'PBKDF2' }, false, ['deriveBits'])
            const rawPrivateEcKeyAB = await deriveRawPrivateFunc(saltAB, passphraseCK)
            // convert to PKCS#8
            const pkcs8nopubAB = new Uint8Array([ ...hex2ab(prefixHex), ...new Uint8Array(rawPrivateEcKeyAB)])
            const algo = { name: 'ECDSA', namedCurve: curve }
            const privateKeyCK = await crypto.subtle.importKey('pkcs8', pkcs8nopubAB, algo, true, ['sign'] )
            const pkcs8AB = await crypto.subtle.exportKey('pkcs8', privateKeyCK)
            // get public key
            return {privateKeyCK, pkcs8AB}
    }, []);

    async function deriveRawPrivate(saltAB, passphraseCK){
        console.log("deriveRawPrivate", saltAB, passphraseCK);
        const algo = { name: 'PBKDF2', salt: saltAB, iterations: kdfIterations, hash: kdfHash }
        const rawKeyAB = await crypto.subtle.deriveBits(algo, passphraseCK, size)
        const nBI = BigInt('0x' + orderHex)
        let rawKeyBI = BigInt('0x' + ab2hex(rawKeyAB))
        if (rawKeyBI >= nBI){ // if derived rawKey greater than/equal to order n...
            rawKeyBI = rawKeyBI % nBI; // ...compute rawKey mod n
        }
        const rawKeyHex = rawKeyBI.toString(16).padStart(2*(size/8), '0') // if shorter, pad with 0x00 to fixed size
        return hex2ab(rawKeyHex)
    }

    async function deriveRawPrivateArgon(saltAB, passphraseCK) {
        console.log("deriveRawPrivateArgon", saltAB, passphraseCK);
        return (await argon2id.hash({
            pass: passphraseCK,
            salt: saltAB,
            time: 3,
            mem: 65536,
            parallelism: 2,
            hashLen: 66
        })).hash;
    }

    async function deriveSharedSecret(privateKey, foreignPublicKey): Promise<ArrayBuffer> {
        return await crypto.subtle.deriveBits(
            {
                name: "ECDH",
                public: foreignPublicKey
            },
            privateKey,
            521
        );
    }

    async function getPublicFromPrivate(privateKeyCK){
        console.log("getPublic", privateKeyCK)
        const privatKeyJWK = await crypto.subtle.exportKey('jwk', privateKeyCK)
        delete privatKeyJWK.d
        privatKeyJWK.key_ops = []
        const algo = { name: 'ECDH', namedCurve: curve }
        return crypto.subtle.importKey('jwk', privatKeyJWK, algo, true, [])
    }

  return {
    generateKeyFromPassword,
    sign,
    verify,
    encrypt,
    decrypt,
    generateRandomSalt,
    deriveSharedSecret
  };
}

export default useCryptography;