import magic
from cryptography.hazmat.primitives.asymmetric import ec
from django.contrib.auth.hashers import check_password

from backend.ahs_crypto import ecc
from backend.ahs_crypto.ecc import deserialize_public_key_from_der, deserialize_public_key_from_pem, \
    serialize_public_key_to_pem


def make_private_key(private_key: ec.EllipticCurvePrivateKey, password: bytes = None):
    """
    Hash a private key for secure storage.

    Args:
        private_key (ec.EllipticCurvePrivateKey): The raw private key to hash.
    Returns:
        str: A hashed and encoded private key.
    """
    sys_priv_exists = PrivateKey.objects.exists()
    if not sys_priv_exists:
        raise ValueError("System private key not found. Populate the database with a valid private key."
                         "Alternatively use `python manage.py populate`. ")
    system_private_key = PrivateKey.objects.first()


    # Hash using Django's make_password to leverage hashing backends
    return ecc.serialize_private_key_to_der(private_key, )


def verify_private_key(private_key: ec.EllipticCurvePrivateKey | str | bytes):
    """
    Verify that the provided private key is valid.
    """

    try:
        (private_key)  # Attempt to deserialize the private key
    except ValueError as exc:
        raise ValueError("Invalid private key provided.") from exc


def check_private_key(password, encoded, setter=None, preferred="default"):
    """
    Check if a raw private key matches the stored hashed version.

    Args:
        password (str): The raw private key to check.
        encoded (str): The hashed private key stored in the database.
        setter (callable): Optional function to update the stored hash.
        preferred (str): Preferred hashing algorithm. "default" by default.

    Returns:
        bool: True if the raw private key matches the hash, False otherwise.
    """
    # Validate private key matching through Django's check_password
    return check_password(password, encoded, setter=setter, preferred=preferred)


async def acheck_private_key(password, encoded, setter=None, preferred="default"):
    """
    Asynchronous version of `check_private_key`.

    Args:
        password (str): The raw private key to check.
        encoded (str): The hashed private key stored in the database.
        setter (callable): Optional function to update the stored hash.
        preferred (str): Preferred hashing algorithm. Defaults to "default".

    Returns:
        bool: True if the raw private key matches the hash, False otherwise.
    """
    return check_password(password, encoded, setter=setter, preferred=preferred)


def make_public_key(privatekey: ec.EllipticCurvePrivateKey) -> ec.EllipticCurvePublicKey:
    """
    Generate the public key from a private key.

    Args:
        privatekey (ECCPrivateKey): The private key object.

    Returns:
        str: The serialized public key in PEM format.
    """
    if isinstance(privatekey, ec.EllipticCurvePrivateKey) and ():
        return ecc.generate_public_key(privatekey)
    raise ValueError("Invalid private key object provided.")


def verify_public_key(public_key: ec.EllipticCurvePublicKey | bytes | str):
    """
    Verify that the provided public key is valid.

    Args:
        public_key (str): The public key as a string.

    Raises:
        ValueError: If the public key is not valid or deserialization fails.
    """
    try:
        if isinstance(public_key, bytes):
            deserialize_public_key_from_der(public_key)
        elif isinstance(public_key, str):
            deserialize_public_key_from_pem(public_key)
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            serialize_public_key_to_pem(public_key)
    except ValueError as exc:
        raise ValueError("Invalid public key provided.") from exc


def check_public_key(password, encoded, setter=None, preferred="default"):
    """
    Check if a public key matches the stored hashed version.

    Args:
        password (str): The raw public key to check.
        encoded (str): The hashed public key stored in the database.
        setter (callable): Optional function to update the stored hash.
        preferred (str): Preferred hashing algorithm. Defaults to "default".

    Returns:
        bool: True if the public key matches the hash, False otherwise.
    """
    # Same as private key, leverage Django's check_password
    return check_password(password, encoded, setter=setter, preferred=preferred)


async def acheck_public_key(password, encoded, setter=None, preferred="default"):
    """
    Asynchronous version of `check_public_key`.

    Args:
        password (str): The raw public key to check.
        encoded (str): The hashed public key stored in the database.
        setter (callable): Optional function to update the stored hash.
        preferred (str): Preferred hashing algorithm. Defaults to "default".

    Returns:
        bool: True if the public key matches the hash, False otherwise.
    """
    return check_password(password, encoded, setter=setter, preferred=preferred)
