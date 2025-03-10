import {useCallback, useEffect, useRef, useState} from "react";
import {IDBPDatabase, openDB} from "idb";


interface IndexedDB {
    storePrivateKey: (privateKey: any) => Promise<void>;
    storePublicKey: (publicKey: any) => Promise<void>;
    storeServerPublicKey: (serverPublicKey: any) => Promise<void>;
    getPrivateKey: () => Promise<string|null>;
    getServerPublicKey: () => Promise<string|null>;
    getPublicKey: () => Promise<string|null>;
}

interface KeyRecord {
  id: string;
  keyData: any;
  created: string;
}


export const useIndexedDB = (): IndexedDB => {
    const dbName = useRef<string>('ahs').current;
    const [database, setDatabase] = useState<IDBPDatabase>(null);


    useEffect(() => {
        initDatabase()
            .then(r => console.log("IndexedDB initialized ", r));

        return () => {
            deleteDatabase()
                .then(r => console.log("Deleted Indexed database ", r))
        }
    }, []);

    async function initDatabase() {
        console.log("Initializing database...");
        const db = await openDB('ahs', 1, {
            upgrade(db) {
                // Create an object store called 'keys' with a keyPath of 'id'
                db.createObjectStore('keys', { keyPath: 'id' });
            }
        });
        setDatabase(db)
    }

    async function deleteDatabase(): Promise<void> {
        await indexedDB.deleteDatabase(dbName);
    }

      // Stores a private key record.
  const storePrivateKey = useCallback(
    async (privateKey: any) => {
      if (!database) throw new Error("Database not initialized");
      try {
        const tx = database.transaction("keys", "readwrite");
        const store = tx.objectStore("keys");
        const record: KeyRecord = {
          id: "privateKey",
          keyData: privateKey,
          created: new Date().toISOString(),
        };
        await store.put(record);
        await tx.done;
      } catch (error) {
        console.error("Error storing private key:", error);
        throw error;
      }
    },
    [database]
  );

  // Stores a public key record.
  const storePublicKey = useCallback(
    async (publicKey: any) => {
      if (!database) throw new Error("Database not initialized");
      try {
        const tx = database.transaction("keys", "readwrite");
        const store = tx.objectStore("keys");
        const record: KeyRecord = {
          id: "publicKey",
          keyData: publicKey,
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

  // Stores a client public key record.
  const storeServerPublicKey = useCallback(
    async (serverPublicKey: any) => {
      if (!database) throw new Error("Database not initialized");
      try {
        const tx = database.transaction("keys", "readwrite");
        const store = tx.objectStore("keys");
        const record: KeyRecord = {
          id: "serverPublicKey",
          keyData: serverPublicKey,
          created: new Date().toISOString(),
        };
        await store.put(record);
        await tx.done;
      } catch (error) {
        console.error("Error storing client public key:", error);
        throw error;
      }
    },
    [database]
  );

  // Retrieves a private key record by id.
  const getPrivateKey = useCallback(
    async (): Promise<any | null> => {
      if (!database) throw new Error("Database not initialized");
      try {
        const tx = database.transaction("keys", "readonly");
        const store = tx.objectStore("keys");
        const record: KeyRecord = await store.get("privateKey");
        await tx.done;
        return record ? record.keyData : null;
      } catch (error) {
        console.error("Error retrieving private key:", error);
        throw error;
      }
    },
    [database]
  );

  // Retrieves a public key record by id.
  const getPublicKey = useCallback(
    async (): Promise<any | null> => {
      if (!database) throw new Error("Database not initialized");
      try {
        const tx = database.transaction("keys", "readonly");
        const store = tx.objectStore("keys");
        const record: KeyRecord = await store.get("publicKey");
        await tx.done;
        return record ? record.keyData : null;
      } catch (error) {
        console.error("Error retrieving public key:", error);
        throw error;
      }
    },
    [database]
  );

  // Retrieves a client public key record by id.
  const getServerPublicKey = useCallback(
    async (): Promise<any | null> => {
      if (!database) throw new Error("Database not initialized");
      try {
        const tx = database.transaction("keys", "readonly");
        const store = tx.objectStore("keys");
        const record: KeyRecord = await store.get('serverPublicKey');
        await tx.done;
        return record ? record.keyData : null;
      } catch (error) {
        console.error("Error retrieving client public key:", error);
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
    }
}

export default useIndexedDB;