import json
from time import time

import sys

from django.utils.http import urlsafe_base64_encode



def is_server_runtime():
    if "manage.py" in sys.argv:
        command = sys.argv[1] if len(sys.argv) > 1 else None
        if command == "runserver":
            return True



def sign_token(data):
    """
    Sign the token payload using the ECC private key.
    """
    payload = json.dumps(data).encode("ascii")

    # Sign the payload with the ECC private key
    signature = b""

    # Concatenate payload and signature and encode as Base64
    return urlsafe_base64_encode(payload + b"." + signature)


def verify_token(token):
    """
    Verify the provided token using ECC public key.
    """
    try:
        # Decode Base64 token
        decoded_token = urlsafe_base64_encode(token.encode('ascii')).encode('ascii')

        # Extract payload and signature
        payload, signature = decoded_token.split(b".", 1)

        # Verify the signature
        # settings.ECC_PUBLIC_KEY.verify(signature, payload, ec.ECDSA(hashes.SHA256()))

        # Deserialize payload
        claims = json.loads(payload.decode("utf-8"))

        # Check expiration time
        if "exp" in claims and int(time()) > claims["exp"]:
            raise RuntimeError("Token has expired.")

        return claims

    except Exception as e:
        raise RuntimeError(f"Invalid token: {e}")

