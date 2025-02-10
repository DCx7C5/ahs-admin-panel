import { useState, useCallback } from 'react';
import * as EC from 'elliptic';


const ellipticCurve = new EC.ec('secp256k1');

interface ECCKeyPair {
  privateKey: string;
  publicKey: string;
}

export const useECC = () => {
  const [keyPair, setKeyPair] = useState<ECCKeyPair | null>(null);

  // Generate ECC key pair
  const generateKeys = useCallback(() => {
    const key = ellipticCurve.genKeyPair();
    const publicKey = key.getPublic('hex');
    const privateKey = key.getPrivate('hex');
    setKeyPair({ privateKey, publicKey });
    return { publicKey, privateKey };
  }, []);

  // Sign a message
  const signMessage = useCallback((message: string, privateKey: string) => {
    const key = ellipticCurve.keyFromPrivate(privateKey);
    const signature = key.sign(message);
    return signature.toDER('hex');
  }, []);

  // Verify a signature
  const verifySignature = useCallback(
    (message: string, signature: string, publicKey: string) => {
      const key = ellipticCurve.keyFromPublic(publicKey, 'hex');
      return key.verify(message, signature);
    },
    []
  );

  // Encrypt a message (simplified example; ECC is not meant for direct encryption)
  const encryptMessage = useCallback(
    (message: string, publicKey: string) => {
      const key = ellipticCurve.keyFromPublic(publicKey, 'hex');
      const encrypted = Buffer.from(message).toString('base64'); // Simplified
      return encrypted;
    },
    []
  );

  // Decrypt a message (basically reverse base64 here for example purposes)
  const decryptMessage = useCallback(
    (encryptedMessage: string, privateKey: string) => {
      const key = ellipticCurve.keyFromPrivate(privateKey, 'hex');
      const decrypted = Buffer.from(encryptedMessage, 'base64').toString(); // Simplified
      return decrypted;
    },
    []
  );

  return {
    keyPair,
    generateKeys,
    signMessage,
    verifySignature,
    encryptMessage,
    decryptMessage,
  };
};