from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import json
import base64
import time
from typing import Dict, Any, Optional
import secrets


class ECCSessionMiddleware:
    def __init__(self, secret_key: str, cookie_name: str = "session", max_age: int = 86400):
        """
        Initialize the ECC Session Middleware

        Args:
            secret_key: Server's secret key for session signing
            cookie_name: Name of the session cookie
            max_age: Maximum age of the session in seconds (default: 24 hours)
        """
        self.cookie_name = cookie_name
        self.max_age = max_age

        # Generate server's static key pair
        self._private_key = ec.derive_private_key(
            int.from_bytes(secret_key.encode(), byteorder='big') % 2 ** 256,
            ec.SECP256K1()
        )
        self.public_key = self._private_key.public_key()

    def _derive_session_key(self, shared_key: bytes) -> bytes:
        """Derive a session key using HKDF"""
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"session_key"
        )
        return hkdf.derive(shared_key)

    def _encrypt_session_data(self, data: Dict[str, Any], ephemeral_private: ec.EllipticCurvePrivateKey) -> str:
        """
        Encrypt session data using AESGCM with perfect forward secrecy

        Args:
            data: Dictionary containing session data
            ephemeral_private: Ephemeral private key for this session

        Returns:
            Encrypted session data as a base64 string
        """
        # Add timestamp for expiry checking
        data['_timestamp'] = int(time.time())

        # Generate shared key
        shared_key = ephemeral_private.exchange(
            ec.ECDH(),
            self.public_key
        )

        # Derive session key
        session_key = self._derive_session_key(shared_key)

        # Serialize and encrypt data
        nonce = secrets.token_bytes(12)
        aesgcm = AESGCM(session_key)

        plaintext = json.dumps(data).encode()
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # Combine ephemeral public key, nonce, and ciphertext
        ephemeral_public_bytes = ephemeral_private.public_key().public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.CompressedPoint
        )

        combined = ephemeral_public_bytes + nonce + ciphertext
        return base64.urlsafe_b64encode(combined).decode()

    def _decrypt_session_data(self, encrypted_data: str) -> Optional[Dict[str, Any]]:
        """
        Decrypt session data

        Args:
            encrypted_data: Base64-encoded encrypted session data

        Returns:
            Decrypted session data as dictionary or None if invalid/expired
        """
        try:
            # Decode combined data
            combined = base64.urlsafe_b64decode(encrypted_data.encode())

            # Extract components
            ephemeral_public_bytes = combined[:33]  # X962 compressed point format
            nonce = combined[33:45]
            ciphertext = combined[45:]

            # Load ephemeral public key
            ephemeral_public = serialization.load_der_public_key(ephemeral_public_bytes)

            # Generate shared key
            shared_key = self._private_key.exchange(
                ec.ECDH(),
                ephemeral_public
            )

            # Derive session key
            session_key = self._derive_session_key(shared_key)

            # Decrypt data
            aesgcm = AESGCM(session_key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            data = json.loads(plaintext)

            # Check expiry
            if int(time.time()) - data['_timestamp'] > self.max_age:
                return None

            del data['_timestamp']
            return data

        except Exception:
            return None

    async def __call__(self, request, call_next):
        """ASGI middleware implementation"""
        # Try to load existing session
        session_data = {}
        if self.cookie_name in request.cookies:
            decrypted = self._decrypt_session_data(request.cookies[self.cookie_name])
            if decrypted:
                session_data = decrypted

        # Attach session to request
        request.session = session_data

        # Process request
        response = await call_next(request)

        # Update session cookie if data changed
        if session_data:
            ephemeral_private, _ = self._generate_ephemeral_keypair()
            encrypted = self._encrypt_session_data(session_data, ephemeral_private)
            response.set_cookie(
                self.cookie_name,
                encrypted,
                max_age=self.max_age,
                httponly=True,
                secure=True,
                samesite='lax'
            )
        elif self.cookie_name in request.cookies:
            response.delete_cookie(self.cookie_name)

        return response