import cbor2
from asgiref.sync import sync_to_async
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from django.conf import settings
from webauthn.helpers import decode_credential_public_key, decoded_public_key_to_cryptography

from webauthn.helpers.cose import COSEAlgorithmIdentifier


RP_NAME = settings.SITE_NAME
EXPECTED_RP_ID = settings.DOMAIN_NAME
EXPECTED_ORIGIN = [f"https://{host}" for host in settings.ALLOWED_HOSTS]
SUPPORTED_ALGOS = [
    COSEAlgorithmIdentifier.EDDSA,
    COSEAlgorithmIdentifier.ECDSA_SHA_512,
    COSEAlgorithmIdentifier.ECDSA_SHA_256,
    COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,
    COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_512,
]


def convert_publickey_pem_to_cbor(pubkey: bytes) -> bytes:
    """
    Convert a PEM-encoded public key to CBOR format.

    This function accepts a PEM-encoded public key, processes it to determine whether it is an RSA or EC
    public key, and transforms it into its COSE Key representation in CBOR format. The COSE Key fields
    (e.g., key type, algorithm, curve, key parameters) are mapped according to the recognized cryptographic
    specifications. If the key type or elliptic curve is unsupported, a ValueError is raised.

    :param pubkey: The PEM-encoded public key.
    :raises ValueError: If the key type or elliptic curve is unsupported, or if the public key format
        is unrecognized.
    :return: COSE Key represented in CBOR format as bytes.
    """
    public_key = serialization.load_pem_public_key(pubkey)
    numbers = public_key.public_numbers()
    if isinstance(numbers, rsa.RSAPublicNumbers):
        # RSA handling
        cose_key = {
            1: 3,  # RSA key type
            3: -37,  # Algorithm (e.g., RSASSA-PSS-SHA256)
            -1: numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big"),  # Modulus (n)
            -2: numbers.e.to_bytes((numbers.e.bit_length() + 7) // 8, "big"),  # Exponent (e)
        }
    elif isinstance(numbers, ec.EllipticCurvePublicNumbers):
        # EC handling
        curve = numbers.curve
        if curve.name == "secp256r1":
            cose_curve = 1  # P-256
            alg = -7  # ES256: ECDSA w/ SHA-256
        elif curve.name == "secp521r1":
            cose_curve = 3  # P-521
            alg = -36  # ES512: ECDSA w/ SHA-512
        else:
            raise ValueError("Unsupported elliptic curve.")

        cose_key = {
            1: 2,  # EC2 key type
            3: alg,  # Algorithm
            -1: cose_curve,  # Curve
            -2: numbers.x.to_bytes((numbers.curve.key_size + 7) // 8, "big"),  # x coordinate
            -3: numbers.y.to_bytes((numbers.curve.key_size + 7) // 8, "big"),  # y coordinate
        }
    else:
        raise ValueError("Unsupported key type or unrecognized public key format.")

    return cbor2.dumps(cose_key)


async def aconvert_publickey_pem_to_cbor(pubkey: bytes) -> bytes:
    return await sync_to_async(convert_publickey_pem_to_cbor)(pubkey)


def convert_publickey_cbor_to_pem(pubkey: bytes) -> bytes:
    """
    Convert a public key from CBOR format to PEM format

    This function decodes a public key in CBOR format using
    `decode_credential_public_key`, transforms it into a cryptographic key object
    using `decoded_public_key_to_cryptography`, and finally converts it to PEM
    format using cryptographic libraries.

    Parameters:
        pubkey (bytes): A public key encoded in CBOR format.

    Returns:
        bytes: The public key converted and encoded in PEM format.

    Raises:
        Any exceptions raised during the process of decoding or transformation
        through the helper functions or cryptography library.
    """
    dec_pubkey = decode_credential_public_key(pubkey)
    crypto_pubkey = decoded_public_key_to_cryptography(dec_pubkey)

    pem_pubkey = crypto_pubkey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pem_pubkey


async def aconvert_publickey_cbor_to_pem(pubkey: bytes) -> bytes:
    return await sync_to_async(convert_publickey_cbor_to_pem)(pubkey)
