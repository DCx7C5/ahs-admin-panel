import {useCallback, useEffect, useRef, useState} from "react";
import {ab2hex, base64UrlEncode, hex2ab} from "../components/utils";
import {IDBPDatabase, openDB} from "idb";

const curve = 'P-521'
const orderHex = '01fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff' +
    'a51868783bf2f966b7fcc0148f709a5d03bb5c9b8899c47aebb6fb71e91386409'
const prefixHex = '3060020100301006072a8648ce3d020106052b81040023044930470201010442'



export interface cryptoApi {
    encrypt: (data: (ArrayBuffer | ArrayBufferView)) => Promise<string>,
    decrypt: (encryptedPayload: string) => Promise<string>,
    sign: (data: (ArrayBuffer | ArrayBufferView | string)) => Promise<null | string>,
    verify: (data: (string), signature: string) => Promise<boolean>,
    persistentStorage: boolean,
    setServerPublicKey: (serverPublicKey: string) => Promise<void>,
    getServerPublicKey: () => Promise<CryptoKey | null>,
    generateRandomSalt: () => string,
    generateKeyFromPassword: (password: string, salt: string, type: "argon" | "pbkdf2") => Promise<CryptoKey>,
    getPublicKeyFromDerivedPasswordKey: (derivedKey: CryptoKey) => Promise<ArrayBuffer>,
    keysGenerated: boolean,
    cryptoKeyToArrayBufferFromJWK: (key: CryptoKey) => Promise<ArrayBuffer>,
    cryptoKeyToArrayBuffer: (key: CryptoKey) => Promise<ArrayBuffer>,
}

export interface KeyRecord {
    id: string,
    keyData: CryptoKey,
    created: string,
}

export const useECCryptography = (): cryptoApi  => {
    const [keysGenerated, setKeysGenerated] = useState<boolean>(false);
    const [database, setDatabase] = useState<IDBPDatabase | null>(null);
    const [persistentStorage, setPersistentStorage] = useState<boolean>(true);
    const dbInitialized = useRef<boolean>(false);
    const {size, kdfHash, kdfIterations} = useRef({
        size: hex2ab(orderHex).byteLength * 8,
        kdfHash: 'SHA-256',
        kdfIterations: 1000000,
    }).current

    useEffect(() => {
      // Initialize Database on mount
      if (!dbInitialized.current) {
        initDatabase().then(r => {
          console.log('Initialized indexedDB...');
        });
        dbInitialized.current = true;
      }
      // Check if keys are generated
      checkKeysGenerated()

      return () => {
          if (!persistentStorage) {
            deleteDatabase().then(r => keysGenerated && console.log("Deleted indexedDB..."));
            setKeysGenerated(false)
          }
      }
    }, []);

    async function initDatabase() {
        const db = await openDB("ahs", 1, {
            upgrade(db) {
            db.createObjectStore("keys", { keyPath: "id" });
          },
        });
        setDatabase(db);
    }

    async function deleteDatabase(): Promise<void> {
        if (!database) return
        await database.deleteObjectStore('keys');
    }

    async function storeToDb(keyType: string, key: CryptoKey): Promise<void> {
        if (!database) throw new Error("Database not initialized");

        try {
          const tx = database.transaction("keys", "readwrite");
          const store = tx.objectStore("keys");
          const record: KeyRecord = {
              id: keyType,
              keyData: key,
              created: new Date().toISOString(),
          };
          await store.put(record);
          await tx.done;
        } catch (error) {
          console.error(`Error storing ${keyType} key:`, error);
          throw error;
        }
      }

    async function retrieveFromDb(keyType: string):Promise<CryptoKey | null> {
        if (!database) return ;
        try {
          const tx = database.transaction("keys", "readonly");
          const store = tx.objectStore("keys");
          const record: KeyRecord = await store.get(keyType);
          await tx.done;
          if (record && record.keyData) {
            // Adjust algorithm parameters based on your key type (e.g., ECDH, RSA)
            return record.keyData
          }
            return null;
          } catch (error) {
            console.error(`Error retrieving ${keyType} key:`, error);
            throw error;
          }
    }

    function checkKeysGenerated() {
        if (retrieveFromDb('serverEcdsa') &&
            retrieveFromDb('serverEcdh') &&
            retrieveFromDb('decryption')) {
            setKeysGenerated(true);
        }
    }

    const sign = useCallback(async (data: ArrayBuffer | ArrayBufferView | string) => {
        try {
            const privateKey = await retrieveFromDb('signing');
            if (!privateKey) {
                console.error("Signing key not found");
                return null; // Return null if the key is missing
            }

            // Convert string data into Uint8Array
            let dataToSign: ArrayBuffer | ArrayBufferView | string = data;

            if (typeof dataToSign === 'string') {
                const encoder = new TextEncoder();
                dataToSign = encoder.encode(dataToSign);
            }

            const signature = await crypto.subtle.sign(
                { name: 'ECDSA', hash: { name: kdfHash } },
                privateKey,
                dataToSign
            );

            return base64UrlEncode(new Uint8Array(signature)); // Return signature as a URL-safe Base64 string
        } catch (error) {
            console.error("Error signing data:", error);
            // Return null to indicate that signing failed
            return null;
        }
    }, []);

    const verify = useCallback(async (data: string, signature: string) => {
        try {
            const verificationKey = await retrieveFromDb('serverEcdsa')
            if (!verificationKey) {
                console.error("Verification key not found")
                return null
            }
            const encoder = new TextEncoder();
            let dataA = encoder.encode(data);
            let signatureA = encoder.encode(signature);

            return await crypto.subtle.verify(
                {name: 'ECDSA', hash: {name: kdfHash}},
                verificationKey,
                signatureA,
                dataA
            );
        } catch (error) {
            console.error("Error verifying signature:", error);
            return null;
        }
    }, []);

    const encrypt = useCallback(async (data: ArrayBuffer | ArrayBufferView) => {
        try {
            const privateKey = await retrieveFromDb('encryption');
            const serverPublicKey = await retrieveFromDb('serverEcdh');

            if (!privateKey) {
                console.error("Keys are missing for encryption");
                return null
            }

            const sharedSecret = await crypto.subtle.deriveBits(
                { name: 'ECDH', public: serverPublicKey },
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
            return null;
        }
    }, []);

    const decrypt = useCallback(async (encryptedPayload: string) => {
        try {
            const privateKey = await retrieveFromDb('decryption');
            const foreignPublicKey = await retrieveFromDb('server');

            if (!privateKey) {
                console.error("Keys are missing for decryption");
                return null
            }

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
    }, [database]);

    const generateRandomSalt = useCallback(
        () => {
            const random = crypto.getRandomValues(new Uint8Array(48));
            return base64UrlEncode(String.fromCharCode(...random))
    }, [])

    const generateKeyFromPassword = async (password: string, salt: string, type: "argon" | "pbkdf2" = "pbkdf2") => {
        const textEncoder = new TextEncoder();
        try {
            const saltAB = textEncoder.encode(salt);
            const passphraseCK = await crypto.subtle.importKey(
                'raw', textEncoder.encode(password),
                { name: 'PBKDF2' },
                true,
                ['deriveBits', 'deriveKey'],
            );
            const rawPrivateEcKeyAB = await deriveRawPrivate(saltAB, passphraseCK);
            const pkcs8nopubAB = new Uint8Array([ ...hex2ab(prefixHex), ...new Uint8Array(rawPrivateEcKeyAB)])
            const algo = { name: 'ECDSA', namedCurve: curve }
            const privateKeyCK = await crypto.subtle.importKey('pkcs8', pkcs8nopubAB, algo, true, ['sign'] )
            await storeToDb('signing', privateKeyCK)
            return privateKeyCK

        } catch (error) {
            console.error("Error generating key from password:", error);
            throw error; // Ensure no retries or loops happen implicitly
        }
    }

    const generateKeyPair = useCallback(async () => {
        const ecdh = { name: 'ECDH', namedCurve: curve }
        const ecdsa = { name: 'ECDSA', namedCurve: curve }

        const ecdhPair = await crypto.subtle.generateKey(ecdh, true, ['deriveBits'])
        const ecdsaPair = await crypto.subtle.generateKey(ecdsa, true, ['sign', 'verify'])
        await storeToDb('ecdsaP', keyPair.privateKey)
        return keyPair
    }, [])

    const deriveRawPrivate = async (salt: ArrayBuffer, passphraseCK: CryptoKey) => {
        const algo = { name: 'PBKDF2', salt: salt, iterations: kdfIterations, hash: kdfHash }
        const rawKeyAB = await crypto.subtle.deriveBits(algo, passphraseCK, size)
           const nBI = BigInt('0x' + orderHex);
           let rawKeyBI = BigInt('0x' + ab2hex(rawKeyAB));

           if (rawKeyBI >= nBI) {
               rawKeyBI = rawKeyBI % nBI;
           }

           if (rawKeyBI < BigInt(0)) {
               throw new Error("Derived key is invalid: less than 0"); // Make issues visible
           }
        const rawKeyHex = rawKeyBI.toString(16).padStart(2*(size/8), '0') // if shorter, pad with 0x00 to fixed size
        return hex2ab(rawKeyHex)
    }

    const getServerVerificationKey = async () => {
        return await retrieveFromDb('serverEcdsa')
    }

    const getServerDecryptionKey = async () => {
        return await retrieveFromDb('serverEcdh')
    }

    const getPrivateEncryptionKey = async () => {
        return await retrieveFromDb('encryption')
    }

    const deriveSharedSecret = async (): Promise<ArrayBuffer | null> => {
        const foreignPublicKey = await retrieveFromDb('serverEcdh');
        const privateKey = await retrieveFromDb('privateEcdh');
        if (!privateKey || !foreignPublicKey) return null;
        return await crypto.subtle.deriveBits(
            {
                name: "ECDH",
                public: foreignPublicKey,
            },
            privateKey,
            521
        );
    }

    const getPublicKeyFromDerivedPasswordKey = async (derivedKey: CryptoKey): Promise<ArrayBuffer> => {
        if (!derivedKey) {
            throw new Error("Derived key cannot be null");
        }

        // Algorithm definition to generate key pair or public key
        const algo = { name: 'ECDH', namedCurve: curve };

        try {
                // Create a new key pair using the derived key as input
                crypto.subtle.deriveKey(algo, derivedKey, algo, true, ['deriveKey'])
                // Export the public key in SPKI format
                return await crypto.subtle.exportKey('spki', keyPair.publicKey);
            } catch (error) {
                console.error("Error deriving public key:", error);
                throw error;
            }
    }

    const cryptoKeyToArrayBuffer = async (key: CryptoKey): Promise<ArrayBuffer> => {
      const format = key.type === 'private' ? 'pkcs8' : 'spki';
      try {
        return  await window.crypto.subtle.exportKey(format, key);
      } catch (error) {
        console.error("Failed to export CryptoKey to ArrayBuffer:", error);
        throw error;
      }
    }

    const cryptoKeyToArrayBufferFromJWK = async (key: CryptoKey): Promise<ArrayBuffer> => {
      try {
        // Export the CryptoKey in JWK format
        const jwk = await crypto.subtle.exportKey("jwk", key);
        // Convert the JWK object to a JSON string
        const jsonString = JSON.stringify(jwk);
        // Encode the JSON string to an ArrayBuffer
        const encoder = new TextEncoder();
        return encoder.encode(jsonString);
      } catch (error) {
        console.error("Failed to export CryptoKey in JWK format:", error);
        throw error;
      }
    }

    const getServerPublicKey = async () => {
        const serverPublicKey = await retrieveFromDb('serverEcdsa')
        if (!serverPublicKey) {
            console.error("Server public key not found")
            return null
        }
        return serverPublicKey
    }

async function setServerPublicKey(serverPublicKeyPem: string): Promise<void> {
      // Step 1: Clean PEM key (remove headers and newlines)
      const pemHeader = "-----BEGIN PUBLIC KEY-----";
      const pemFooter = "-----END PUBLIC KEY-----";
      const pemContents = serverPublicKeyPem
        .replace(pemHeader, "")
        .replace(pemFooter, "")
        .replace(/\s/g, ""); // Remove whitespaces and newlines

      // Step 2: Decode Base64 to ArrayBuffer
      const binaryDerString = atob(pemContents);
      const binaryDer = new Uint8Array(binaryDerString.length);
      for (let i = 0; i < binaryDerString.length; i++) {
        binaryDer[i] = binaryDerString.charCodeAt(i);
      }

      // Step 3: Import the CryptoKey
      const ecdsaKey = await crypto.subtle.importKey(
        "spki", // Public keys use "spki" (SubjectPublicKeyInfo) format
        binaryDer.buffer, // ArrayBuffer of the key
        {
          name: "ECDSA", // Elliptic Curve Digital Signature Algorithm
          namedCurve: curve, // Curve name (e.g., "P-521")
        },
        true, // Extractable key
        ["verify"] // Key usage: "verify" for signature verification
      );

      const ecdhKey = await crypto.subtle.importKey(
          "spki",
          binaryDer.buffer,
          {
              name: "ECDH",
              namedCurve: curve,
          },
          true,
          ["deriveKey"]
      )

      // Step 4: Store or use the key
      console.log("Successfully imported server public key", ecdsaKey, ecdhKey);
      await storeToDb("serverEcdsa", ecdsaKey);
      await storeToDb("serverEcdh", ecdhKey);
    }

    return {
        encrypt,
        decrypt,
        sign,
        verify,
        keysGenerated,
        generateRandomSalt,
        persistentStorage,
        getServerPublicKey,
        setServerPublicKey,
        generateKeyFromPassword,
        getPublicKeyFromDerivedPasswordKey,
        cryptoKeyToArrayBuffer,
        cryptoKeyToArrayBufferFromJWK,
    };
}

export default useECCryptography;