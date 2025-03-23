import {useCallback, useEffect, useRef, useState} from "react";
import {IDBPDatabase, openDB} from "idb";


export interface IndexedDB {
  storeKey: (keyType: string, key: CryptoKey) => Promise<void>;
  getKey: (keyType: string) => Promise<CryptoKey | null>;
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
    initDatabase().then(r => console.log("Initialized database..."));
    return () => {
      deleteDatabase().then(r => console.log("Deleted database..."));
    };
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
    await database?.deleteObjectStore(dbName);
  }

  const store = async (keyType: string, key: CryptoKey): Promise<void> => {
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
      console.error("Error storing signing key:", error);
      throw error;
    }
  }

  const retrieve = async (keyType: string):Promise<CryptoKey | null> => {
    if (!database) throw new Error("Database not initialized");
    try {
      const tx = database.transaction("keys", "readonly");
      const store = tx.objectStore("keys");
      const record: KeyRecord = await store.get(`${keyType}`);
      await tx.done;
      if (record && record.keyData) {
        // Adjust algorithm parameters based on your key type (e.g., ECDH, RSA)
        return record.keyData
      }
        return null;
      } catch (error) {
        console.error("Error retrieving private key:", error);
        throw error;
      }
  }

  const storeKey = useCallback(async (keyType: string, key: CryptoKey) => {
    if (keyType === "signing") {
      await store(keyType, key)
    } else if (keyType === "verification") {
      await store(keyType, key)
    } else if (keyType === "encryption") {
      await store(keyType, key)
    } else if (keyType === "decryption") {
      await store(keyType, key)
    } else {
      console.error("Key type not supported")
    }
  }, []);

  const getKey = useCallback(async (keyType: string): Promise<CryptoKey | null> => {
    if (keyType === "signing") {
      return await retrieve("signing")
    } else if (keyType === "verification") {
      return await retrieve("verification")
    } else if (keyType === "encryption") {
      return await retrieve("encryption")
    } else if (keyType === "decryption") {
      return await retrieve("decryption")
    } else {
      return null
    }
  }, [database]);

  return {
    storeKey,
    getKey,
  };
};

export default useIndexedDB;