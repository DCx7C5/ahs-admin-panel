import {useCallback, useEffect, useRef, useState} from "react";
import {IDBPDatabase, openDB, StoreValue} from "idb";

// Updated interface to reflect CryptoKey usage
export interface IndexedDB {
  storePrivateKey: (privateKey: CryptoKey, privateKeyAB: ArrayBuffer) => Promise<void>;
  storePublicKey: (publicKey: CryptoKey, publicKeyAB: ArrayBuffer) => Promise<void>;
  storeServerPublicKey: (serverPublicKey: CryptoKey, serverPublicKeyAB: ArrayBuffer) => Promise<void>;
  getPrivateKey: () => Promise<{CryptoKey, ArrayBuffer } | null>;
  getPublicKey: () => Promise<{CryptoKey, ArrayBuffer } | null>;
  getServerPublicKey: () => Promise<{CryptoKey, ArrayBuffer } | null>;
}

export interface KeyRecord {
  id: string;
  keyData: any; // This will hold the exported key (e.g., JWK)
  created: string;
}

export const useIndexedDB = (name: string = "ahs"): IndexedDB => {
  const dbName = useRef<string>(name).current;
  const [database, setDatabase] = useState<IDBPDatabase | null>(null);

  useEffect(() => {
    initDatabase().then();
    return () => {
      deleteDatabase().then();
    };
  }, []);

  async function initDatabase() {
    const db = await openDB("ahs", 1, {
      upgrade(db) {
        db.createObjectStore("keys", { keyPath: "id" });
      },
    });
    setDatabase(db);
    console.log("Initialized database...");
  }

  async function deleteDatabase(): Promise<void> {
    await indexedDB.deleteDatabase(dbName);
  }

  const store = async (keyType: string, key: CryptoKey, keyAB: ArrayBuffer) => {
    if (!database) throw new Error("Database not initialized");
    try {
      const tx = database.transaction("keys", "readwrite");
      const store = tx.objectStore("keys");
      const record: KeyRecord = {
          id: `${keyType}`,
          keyData: key,
          created: new Date().toISOString(),
      };
      const record2: KeyRecord = {
          id: `${keyType}AB`,
          keyData: keyAB,
          created: new Date().toISOString(),
      };
      await store.put(record);
      await store.put(record2);
      await tx.done;
    } catch (error) {
      console.error("Error storing signing key:", error);
      throw error;
    }
  }

  const retrieve = async (keyType: string) => {

  }

  const storeSigningKey = useCallback((key: CryptoKey) => {
    if (!database) throw new Error("Database not initialized");
    try {
      const tx = database.transaction("keys", "readwrite");
      const store = tx.objectStore("keys");

    } catch (error) {
      console.error("Error storing signing key:", error);
      throw error;
    }

  },[database])

  const storeVerificationKey = useCallback((key: CryptoKey) => {

  },[database])

  const storeEncryptionKey = useCallback((key: CryptoKey) => {

  },[database])

  const storeDecryptionKey = useCallback((key: CryptoKey) => {

  },[database])

  const getSigningKey = useCallback((key: CryptoKey) => {

  },[database])

  const getVerificationKey = useCallback((key: CryptoKey) => {

  },[database])

  const getEncryptionKey = useCallback((key: CryptoKey) => {

  },[database])

  const getDecryptionKey = useCallback((key: CryptoKey) => {

  },[database])


  const storePrivateKey = useCallback(
    async (privateKey: CryptoKey, privateKeyAB: ArrayBuffer) => {
      if (!database) throw new Error("Database not initialized");
      try {
        const tx = database.transaction("keys", "readwrite");
        const store = tx.objectStore("keys");
        const record: KeyRecord = {
          id: "privateKey",
          keyData: privateKey,
          created: new Date().toISOString(),
        };
        const record2: KeyRecord = {
          id: "privateKeyAB",
          keyData: privateKeyAB,
          created: new Date().toISOString(),
        }
        await store.put(record);
        await store.put(record2);
        await tx.done;
      } catch (error) {
        console.error("Error storing private key:", error);
        throw error;
      }
    },
    [database]
  );

  // Store public key by exporting it to JWK format
  const storePublicKey = useCallback(
    async (publicKey: CryptoKey) => {
      if (!database) throw new Error("Database not initialized");
      try {
        const exportedKey = await crypto.subtle.exportKey("jwk", publicKey);
        const tx = database.transaction("keys", "readwrite");
        const store = tx.objectStore("keys");
        const record: KeyRecord = {
          id: "publicKey",
          keyData: exportedKey,
          created: new Date().toISOString(),
        };
        await store.put(record);
        await tx.done;
      } catch (error) {
        console.error("Error storing public key:", error);
        throw error;
      }
    },
    [database]
  );

  // Store server public key by exporting it to JWK format
  const storeServerPublicKey = useCallback(
    async (serverPublicKey: CryptoKey) => {
      if (!database) throw new Error("Database not initialized");
      try {
        const exportedKey = await crypto.subtle.exportKey("jwk", serverPublicKey);
        const tx = database.transaction("keys", "readwrite");
        const store = tx.objectStore("keys");
        const record: KeyRecord = {
          id: "serverPublicKey",
          keyData: exportedKey,
          created: new Date().toISOString(),
        };
        await store.put(record);
        await tx.done;
      } catch (error) {
        console.error("Error storing server public key:", error);
        throw error;
      }
    },
    [database]
  );

  // Retrieve private key and import it from JWK format
  const getPrivateKey = useCallback(
    async (): Promise<KeyRecord | null> => {
      if (!database) throw new Error("Database not initialized");
      try {
        const tx = database.transaction("keys", "readonly");
        const store = tx.objectStore("keys");
        const record: KeyRecord = await store.get("privateKey");
        await tx.done;
        if (record && record.keyData) {
          // Adjust algorithm parameters based on your key type (e.g., ECDH, RSA)
            return record
        }
        return null;
      } catch (error) {
        console.error("Error retrieving private key:", error);
        throw error;
      }
    },
    [database]
  );

  // Retrieve public key and import it from JWK format
  const getPublicKey = useCallback(
    async (): Promise<CryptoKey | null> => {
      if (!database) throw new Error("Database not initialized");
      try {
        const tx = database.transaction("keys", "readonly");
        const store = tx.objectStore("keys");
        const record: KeyRecord = await store.get("publicKey");
        await tx.done;
        if (record && record.keyData) {
            return await crypto.subtle.importKey(
              "jwk",
              record.keyData,
              {name: "ECDH", namedCurve: "P-256"}, // Example: adjust as needed
              true, // extractable
              [] // Public keys typically have no usages
          );
        }
        return null;
      } catch (error) {
        console.error("Error retrieving public key:", error);
        throw error;
      }
    },
    [database]
  );

  // Retrieve server public key and import it from JWK format
  const getServerPublicKey = useCallback(
    async (): Promise<CryptoKey | null> => {
      if (!database) throw new Error("Database not initialized");
      try {
        const tx = database.transaction("keys", "readonly");
        const store = tx.objectStore("keys");
        const record: KeyRecord = await store.get("serverPublicKey");
        await tx.done;
        if (record && record.keyData) {
            return await crypto.subtle.importKey(
              "jwk",
              record.keyData,
              {name: "ECDH", namedCurve: "P-256"}, // Example: adjust as needed
              true, // extractable
              [] // Public keys typically have no usages
          );
        }
        return null;
      } catch (error) {
        console.error("Error retrieving server public key:", error);
        throw error;
      }
    },
    [database]
  );

  return {
    storePrivateKey,
    storePublicKey,
    storeServerPublicKey,
    getPrivateKey,
    getPublicKey,
    getServerPublicKey,
  };
};

export default useIndexedDB;