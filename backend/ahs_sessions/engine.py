import hashlib
import hmac

from django.contrib.sessions.backends.db import SessionStore as DBSessionStore

from backend.ahs_crypto.ecc import decrypt, ecc_encrypt


class ECCSessionStore(DBSessionStore):
    """
    Custom session store that:
    1. Encrypts the session data using ECC.
    2. Hashes it for integrity (like Django's default behavior).
    3. Stores the result in the database.
    """

    def _encrypt_and_hash_session_data(self, session_data):
        """
        Encrypt the session data and then hash it before storing.
        """
        # Step 1: Serialize session data into JSON format
        serialized_data = self.encode(session_data)

        # Step 2: Encrypt the serialized data
        encrypted_data = ecc_encrypt(serialized_data, private_key, public_key)

        # Step 3: Generate a hash of the encrypted data for additional integrity
        hmac_value = hmac.new(secret_key, encrypted_data, hashlib.sha512).hexdigest()

        # Store both the encrypted data and the hash (optional, can include logging)
        return f"{hashed_data}"  # Use a delimiter to separate encrypted data from the hash

    def _decrypt_and_verify_session_data(self, stored_data):
        """
        Decrypt the stored data and verify its integrity using the hash.
        """
        try:
            # Split stored data into encrypted data and its hash
            encrypted_data, stored_hash = stored_data.split("|")

            # Step 1: Verify the stored hash with the hash of the encrypted data
            calculated_hash = hashlib.sha512(encrypted_data.encode('utf-8')).hexdigest()
            if calculated_hash != stored_hash:
                raise ValueError("Hash verification failed! Possible tampering detected.")

            # Step 2: Decrypt the data and return the session data
            decrypted_data = decrypt(encrypted_data, private_key, public_key)

            return self.decode(decrypted_data)  # Deserialize JSON string back to Python data
        except Exception:
            # If decryption or hash verification fails, return an empty session
            return {}

    def save(self, must_create=False):
        """
        Override to encrypt and hash session data before storing in the database.
        """
        if self._session is None:
            return self._session_cache

        # Encrypt and hash the session data
        encrypted_hashed_data = self._encrypt_and_hash_session_data(self._session_cache)

        # Temporarily replace the session cache with encrypted + hashed data
        self._session_cache = encrypted_hashed_data
        super().save(must_create=must_create)

    def load(self):
        """
        Override to decrypt and verify session data from the database.
        """
        encrypted_hashed_data = super().load()
        if encrypted_hashed_data:
            self._session_cache = self._decrypt_and_verify_session_data(encrypted_hashed_data)
        else:
            self._session_cache = {}
        return self._session_cache