import base64
import os
from pathlib import Path
from typing import Literal

import magic

from concurrent.futures import ThreadPoolExecutor
from os import urandom

from asgiref.sync import sync_to_async
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.dh import DHPublicKey
from cryptography.hazmat.primitives.asymmetric.dsa import DSAPublicKey
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateNumbers, EllipticCurvePublicKey, SECP521R1, \
    ECDSA
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed448 import Ed448PublicKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.x448 import X448PublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import GCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.hashes import SHA256, SHA512
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from django.utils.encoding import force_bytes
from django.utils.functional import classproperty, SimpleLazyObject
from django.conf import settings

mime = magic.Magic(mime=True)
executor = ThreadPoolExecutor()

ROOT_PRIVKEY_PATH = os.getenv("ROOT_PRIVKEY_PATH", 'root.private.key')



def get_curve_order(curve):
    """
    Return the order of the given elliptic curve.
    Since `cryptography` doesn't provide curve order, it's manually defined here.
    """
    curve_orders = {
        ec.SECP256R1: 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551,
        ec.SECP521R1: 0x01FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF,
    }
    return curve_orders.get(type(curve), None)


def load_public_key_from_file(file_path: os.PathLike) -> None | DHPublicKey | DSAPublicKey | RSAPublicKey | EllipticCurvePublicKey | Ed25519PublicKey | Ed448PublicKey | X25519PublicKey | X448PublicKey:

    with open(file_path, 'rb') as key_file:
        content = key_file.read()
        mime_type = mime.from_buffer(content)
        if (mime_type == "text/plain") and "PUBLIC" in content.decode('ascii'):
            return deserialize_public_key_from_pem(content)
        elif mime_type == "application/octet-stream":
            return deserialize_public_key_from_der(content)


def load_private_key_from_file(path: os.PathLike, password: str | bytes) -> ec.EllipticCurvePrivateKey:
    if isinstance(password, str):
        password = password.encode('ascii')

    with open(path, 'rb') as key_file:
        buffer = key_file.read()
        mtype = mime.from_buffer(buffer)

        if mtype == "text/plain" and "PRIVATE" in buffer.decode('ascii'):
            return serialization.load_pem_private_key(buffer, password=password)
        elif mtype == "application/octet-stream":
            return serialization.load_der_private_key(buffer, password=password)
        else:
            raise ValueError("Invalid key file format.")

def derive_from_private_root_key(password: str | bytes):
    rootkey_path = ROOT_PRIVKEY_PATH
    privkey = load_private_key_from_file(Path(rootkey_path), password).private_numbers()
    return derive_subkey(privkey, 0)


def save_private_key_to_file(
        private_key: ec.EllipticCurvePrivateKey,
        path: os.PathLike = ROOT_PRIVKEY_PATH,
        password: bytes = None
):
    with open(path, 'wb') as key_file:
        key_file.write(serialize_private_key_to_pem(private_key, password))


def save_public_key_to_file(public_key: ec.EllipticCurvePublicKey, path: os.PathLike = ROOT_PRIVKEY_PATH):
    with open(path, 'wb') as key_file:
        key_file.write(serialize_public_key_to_pem(public_key))


def generate_private_key() -> ec.EllipticCurvePrivateKey:
    return ec.generate_private_key(curve=ECC.default_curve)


def generate_public_key(private_key: ec.EllipticCurvePrivateKey) -> ec.EllipticCurvePublicKey:
    return private_key.public_key()


def create_ecc_keypair():
    private_key = ec.generate_private_key(curve=ECC.default_curve)
    public_key = private_key.public_key()
    return private_key, public_key


def serialize_public_key_to_pem(public_key):
    return public_key.public_bytes(
        encoding=Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def serialize_public_key_to_x962(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint,
    )


def serialize_public_key_to_der(public_key):
    return public_key.public_bytes(
        encoding=Encoding.DER,
        format=serialization.PublicFormat.PKCS1,
    )


def serialize_private_key_to_pem(private_key: ec.EllipticCurvePrivateKey, password: str | bytes = None):
    encryption_algo = serialization.NoEncryption()
    if isinstance(password, str):
        encryption_algo = serialization.BestAvailableEncryption(password.encode('latin-1'))
    elif isinstance(password, bytes):
        encryption_algo = serialization.BestAvailableEncryption(password)

    return private_key.private_bytes(
        encoding=Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algo,
    )


def serialize_private_key_to_der(private_key: ec.EllipticCurvePrivateKey, password: str | bytes = None):
    if isinstance(password, bytes):
        encryption_algorithm = serialization.BestAvailableEncryption(password)
    elif isinstance(password, str):
        encryption_algorithm = serialization.BestAvailableEncryption(password.encode('latin-1'))
    else:
        encryption_algorithm = serialization.NoEncryption()
    return private_key.private_bytes(
        encoding=Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm,
    )


def deserialize_public_key_from_pem(public_key_pem):
    return serialization.load_pem_public_key(public_key_pem)


def deserialize_public_key_from_der(public_key_der):
    return serialization.load_der_public_key(public_key_der)


def deserialize_public_key_from_x962(public_key_x962):
    return serialization.load_der_public_key(public_key_x962)


def deserialize_private_key_from_pem(private_key_pem, password: str | bytes = None) -> ec.EllipticCurvePrivateKey:
    return serialization.load_pem_private_key(private_key_pem, password=password)


def deserialize_private_key_from_der(private_key_der, password: str | bytes = None) -> ec.EllipticCurvePrivateKey:
    return serialization.load_der_private_key(private_key_der, password=password)


def encrypt(data,private_key, public_key):
    # Generate shared key using private and public keys
    shared_key = private_key.exchange(ec.ECDH(), public_key)

    # Derive symmetric key (AES key with HKDF)
    aes_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"session_key",
    ).derive(shared_key)

    # Encrypt the session data using AES
    iv = urandom(16)
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data.encode()) + encryptor.finalize()
    return base64.b64encode(iv + ciphertext).decode("ascii")


def decrypt(encrypted_data, private_key, public_key):
    # Decode the data
    encrypted_data = base64.b64decode(encrypted_data)
    iv = encrypted_data[:16]
    ciphertext = encrypted_data[16:]

    # Generate shared key using both keys
    shared_key = private_key.exchange(ec.ECDH(), public_key)

    # Derive AES key from shared key using HKDF
    aes_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=None,
            info=b"session_key",
    ).derive(shared_key)

    # Decrypt using AES
    cipher = Cipher(AES(aes_key), GCM(iv))
    decryptor = cipher.decryptor()
    return decryptor.update(ciphertext).decode('ascii') + decryptor.finalize().decode("utf-8")


def derive_subkey(private_key: EllipticCurvePrivateNumbers, index: int, curve=ec.SECP521R1()) -> ec.EllipticCurvePrivateKey | None:
    """
    Derive a subkey from a given ECC private key using HMAC for determinism.

    :param private_key: Parent ECC private key (integer or similar format).
    :param index: Integer index for subkey derivation.
    :param curve: Elliptic curve to use (default: SECP521R1).
    :return: Derived private key.
    """
    private_key_int = private_key.private_value
    # Serialize the private key to bytes
    private_key_bytes = private_key_int.to_bytes((private_key_int.bit_length() + 7) // 8, byteorder='big')

    # Use HMAC (or another derivation function) for deterministic subkey generation
    hkdf = HKDF(
        algorithm=SHA256(),
        length=32,  # Output should match the curve requirements
        salt=None,  # Uniqueness is provided by index
        info=b"ECC Hierarchical Key Derivation",  # Contextual binding (HKDF strength)
    )

    # create derivation index
    index_bytes = index.to_bytes(4, byteorder='big')
    deterministically_derived_key = hkdf.derive(private_key_bytes + index_bytes)

    # Convert the derived key into an integer
    derived_key_int = int.from_bytes(deterministically_derived_key, byteorder='big')
    curve_order = get_curve_order(curve)
    if not curve_order:
        raise ValueError(f"Unsupported curve: {type(curve).__name__}")

    derived_key_int = derived_key_int % curve_order
    if derived_key_int == 0:  # Ensure it's a valid private key
        derived_key_int += 1

    return ec.derive_private_key(derived_key_int, ec.SECP521R1())


def get_root_private_key(password: str) -> ec.EllipticCurvePrivateKey | None:
    if password is None:
        raise ValueError("Password is required.")
    if isinstance(password, str):
        password = password.encode('ascii')
    return load_private_key_from_file(Path(ROOT_PRIVKEY_PATH), password=password)


async def agenerate_private_key() -> ec.EllipticCurvePrivateKey:
    async_func = sync_to_async(generate_private_key)
    return await async_func()


async def agenerate_public_key(private_key: ec.EllipticCurvePrivateKey) -> ec.EllipticCurvePublicKey:
    return await sync_to_async(generate_public_key)(private_key)


async def aload_public_key_from_file(file_path: os.PathLike):
    return await sync_to_async(load_public_key_from_file)(file_path)


async def aload_private_key_from_file(path: os.PathLike, password: str | bytes) -> ec.EllipticCurvePrivateKey:
    return await sync_to_async(load_private_key_from_file)(path, password)


async def asave_private_key_to_file(private_key: ec.EllipticCurvePrivateKey, path: os.PathLike, password: bytes = None):
    return await sync_to_async(save_private_key_to_file)(private_key, path, password)


async def asave_public_key_to_file(public_key: ec.EllipticCurvePublicKey, path: os.PathLike):
    return await sync_to_async(save_public_key_to_file)(public_key, path)


async def acreate_ecc_keypair():
    return await sync_to_async(create_ecc_keypair)()


async def aserialize_public_key_to_pem(public_key):
    return await sync_to_async(serialize_public_key_to_pem)(public_key)


async def aencrypt(data, private_key, public_key):
    return await sync_to_async(encrypt)(data, private_key, public_key)


async def adecrypt(encrypted_data, private_key, public_key):
    return await sync_to_async(decrypt)(encrypted_data,private_key, public_key)


async def aderive_subkey(master_private_key: ec.EllipticCurvePrivateKey, index: int):
    return await sync_to_async(derive_subkey)(master_private_key.private_numbers(), index, ec.SECP521R1())


def derive_key_from_string(input_string, salt, iterations: int = 500000) -> ec.EllipticCurvePrivateKey:
    """
    Derive an EllipticCurvePrivateKey from a passphrase and salt.

    :param input_string: The passphrase to generate the key deterministically.
    :param salt: A unique cryptographically secure salt (16 bytes minimum recommended).
    :param iterations: The number of iterations for the key derivation function.
    :return: An EllipticCurvePrivateKey instance derived from the string.
    """
    if len(salt) < 16:
        raise ValueError("Salt must be at least 16 bytes.")

    # Convert input string to bytes
    input_bytes = force_bytes(input_string)
    salt = force_bytes(salt)

    # Derive a fixed-length key (e.g., 64 bytes) using PBKDF2
    kdf = PBKDF2HMAC(
        algorithm=SHA512(),
        length=64,  # 512-bit key
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    private_key_bytes = kdf.derive(input_bytes)

    # Convert the derived bytes into an integer to match EC private key requirements
    private_key_int = int.from_bytes(private_key_bytes, byteorder="big")

    # Generate an EllipticCurvePrivateKey from the derived bytes, ensuring its valid
    private_key = ec.derive_private_key(
        private_key_int % ec.SECP521R1().key_size,  # Ensure the private key is within the curve's range
        curve=ec.SECP521R1(),
        backend=default_backend()
    )

    return private_key

async def aderive_key_from_string(input_string: str, salt: bytes, iterations: int = 100000) -> ec.EllipticCurvePrivateKey:
    return await sync_to_async(derive_key_from_string)(input_string, salt, iterations)


def convert(
        key: ec.EllipticCurvePrivateKey | ec.EllipticCurvePublicKey | str | bytes | int | os.PathLike,
        convert_to: Literal['pem', 'der', 'x962', 'int', 'class'] = "bytes"
):
    if isinstance(key, str) and os.path.exists(os.path.abspath(key)):
        with open(key, 'rb') as key_file:
            key_data = key_file.read()
            # Attempt to deserialize public or private keys
            if b'PUBLIC' in key_data:
                try:
                    key = deserialize_public_key_from_pem(key_data)
                except Exception:
                    try:
                        key = deserialize_public_key_from_der(key_data)
                    except Exception as e:
                        raise ValueError(f"Invalid key file format: {e}")
            elif b'PRIVATE' in key_data:
                try:
                    key = deserialize_private_key_from_pem(key_data)
                except Exception:
                    try:
                        key = deserialize_private_key_from_der(key_data)
                    except Exception as e:
                        raise ValueError(f"Invalid key file format: {e}")

    if isinstance(key, (ec.EllipticCurvePrivateKey, ec.EllipticCurvePublicKey)):
        if convert_to == 'pem':
            if isinstance(key, ec.EllipticCurvePrivateKey):
                return serialize_private_key_to_pem(key)
            else:
                return serialize_public_key_to_pem(key)
        elif convert_to == 'der':
            if isinstance(key, ec.EllipticCurvePrivateKey):
                return serialize_private_key_to_der(key)
            else:
                return serialize_public_key_to_der(key)
        elif convert_to == 'x962' and isinstance(key, ec.EllipticCurvePublicKey):
            return serialize_public_key_to_x962(key)
        elif convert_to == 'x962' and isinstance(key, ec.EllipticCurvePrivateKey):
            raise ValueError("Private key cannot be serialized to X9.62 format.")

        elif convert_to == 'int' and isinstance(key, ec.EllipticCurvePrivateKey):
            return key.private_numbers().private_value
        elif convert_to == 'class':
            return key  # Return the object itself for 'class' conversion
    elif isinstance(key, bytes):
        return key
    elif isinstance(key, str):
        return force_bytes(key)
    elif isinstance(key, int):
        return key.to_bytes((key.bit_length() + 7) // 8, 'big')

    raise ValueError(f"Invalid key type or conversion format: key={type(key)}, convert_to={convert_to}")


async def aconvert(
        key: ec.EllipticCurvePrivateKey | ec.EllipticCurvePublicKey | str | bytes | int | os.PathLike,
        convert_to: Literal['pem', 'der', 'x962', 'int'] = "bytes"
):
    return await sync_to_async(convert)(key, convert_to)



class ECC:

    default_curve = SECP521R1()
    default_sign_algorithm = ECDSA(SHA512())
    default_hash_algorithm = SHA512()

    _root_private_key: ec.EllipticCurvePrivateKey | None = None
    _root_public_key: ec.EllipticCurvePublicKey | None = None

    @classproperty
    def root_private_key(cls):  # noqa
        if cls._root_private_key is None:
            cls._load_keys()
        return cls._root_private_key

    @classproperty
    def root_public_key(cls):  # noqa
        if cls._root_public_key is None:
            cls._load_keys()
        return cls._root_public_key

    @classmethod
    def _load_keys(cls):
        cls._root_private_key = SimpleLazyObject(lambda: derive_key_from_string(settings.RUNTIME_SECRET_KEY, settings.SECRET_KEY.encode()))  # noqa
        cls._root_public_key = cls._root_private_key.public_key()

    @classmethod
    def sign(cls, data):
        return cls._root_private_key.sign(data, cls.default_sign_algorithm)

    @classmethod
    async def asign(cls, data):
        return await sync_to_async(cls.sign)(data)

    @classmethod
    def verify(cls, data, signature):
        return cls._root_public_key.verify(signature, data, cls.default_sign_algorithm)

    @classmethod
    async def averify(cls, data, signature):
        return await sync_to_async(cls.verify)(signature, data)

    @classmethod
    def get_shared_secret(cls, client_public_key: EllipticCurvePublicKey):
        return cls._root_private_key.exchange(ec.ECDH(), client_public_key).decode('ascii')
