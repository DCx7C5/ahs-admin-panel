from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, EllipticCurvePublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey
from django.core.exceptions import ImproperlyConfigured

from typing_extensions import TypeVar

from backend.ahs_core.utils import get_crypto_backend as _get_crypto_backend

_CryptoBackend = _get_crypto_backend()


_PrivateKeyType = TypeVar("_PrivateKeyType", EllipticCurvePrivateKey, RSAPrivateKey)
_PublicKeyType = TypeVar("_PublicKeyType", EllipticCurvePublicKey, RSAPublicKey)


def get_server_public_key() -> _PublicKeyType:
    pub = _CryptoBackend.root_public_key
    if not pub:
        raise ImproperlyConfigured("Server public key not found")
    return pub


def get_server_private_key() -> _PrivateKeyType:
    priv = _CryptoBackend.root_private_key
    if not priv:
        raise ImproperlyConfigured("Server private key not found")
    return priv


def verify_signature(signature: bytes, data: bytes):
    return _CryptoBackend.root_public_key.verify(signature, data, _CryptoBackend.ec_signature_algorithm)

def sign_data(data: bytes):
    return _CryptoBackend.root_private_key.sign(data, _CryptoBackend.ec_signature_algorithm)
