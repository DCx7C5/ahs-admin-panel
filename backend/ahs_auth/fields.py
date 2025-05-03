from cryptography.hazmat.primitives.asymmetric import ec, rsa
from django.db import models
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidKey
import cbor2
from webauthn.helpers import decode_credential_public_key, decoded_public_key_to_cryptography
from cryptography.hazmat.primitives.serialization import Encoding


class NameField(models.CharField):
    """
    Custom field that behaves like CharField but also validates a minimum character length.
    """
    def __init__(self, *args, **kwargs):
        self.min_length = kwargs.pop('min_length', None)  # Extract the minimum length parameter
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        """
        Perform validation for the minimum length and call the base class validation.
        """
        if self.min_length is not None and len(value) < self.min_length:
            raise ValueError(
                f"The value for {self.attname} must be at least {self.min_length} characters long."
            )
        # Call the parent class's validate() method
        super().validate(value, model_instance)


class WebAuthnPublicKeyField(models.TextField):
    """
    A custom Django field to store public keys in PEM format and automatically convert to CBOR when accessed.
    """

    description = "A field for storing public keys in PEM format, with automatic CBOR conversion."

    def __init__(self, *args, **kwargs):
        self.validate_on_save = kwargs.pop("validate_on_save", True)  # Optional validation control
        super().__init__(*args, **kwargs)

    def to_python(self, value: str):
        """
        Automatically convert PEM data into WebAuthn-compatible CBOR format.
        Returns a CBOR-encoded version of the public key.
        """
        if not value:
            return None

        try:
            # Load the PEM public key
            public_key = serialization.load_pem_public_key(value.encode())
            numbers = public_key.public_numbers()
            # Convert the public key to WebAuthn (CBOR) format
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

            # CBOR-encode the COSE key
            return cbor2.dumps(cose_key)

        except (ValueError, InvalidKey) as e:
            raise ValueError(f"Error converting PEM to CBOR: {str(e)}")

    def get_prep_value(self, value: bytes):
        """
        Prepare PublicKey for database storage.
        """
        if not value:
            return None

        # Ensure the input is a valid PEM-encoded public key
        try:
            dec_pubkey = decode_credential_public_key(value)
            crypto_pubkey = decoded_public_key_to_cryptography(dec_pubkey)

            pem_pubkey = crypto_pubkey.public_bytes(
                encoding=Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            pem_str = pem_pubkey.decode('utf-8')
        except (ValueError, InvalidKey):
            raise ValueError("Invalid PEM format for public key data.")

        return pem_str

    def validate(self, value, model_instance):
        """
        Validate the PEM format of the public key before saving to the database.
        """
        if self.validate_on_save and value:
            try:
                serialization.load_pem_public_key(value.encode())
            except (ValueError, InvalidKey):
                raise ValueError(f"Invalid public key in {self.attname}.")
        return super().validate(value, model_instance)

    def contribute_to_class(self, cls, name, **kwargs):
        """
        Override the default behavior when the field is added to a model.
        Add a custom descriptor for the field.
        """
        super().contribute_to_class(cls, name, **kwargs)
        setattr(cls, name, self.Descriptor(self))  # Assign custom descriptor to the field


    class Descriptor:
        """
        Custom descriptor to return the CBOR-converted value when the field is accessed.
        """

        def __init__(self, field):
            self.field = field

        def __get__(self, instance, owner):
            if instance is None:
                return self  # Return the descriptor itself for class access
            raw_value = instance.__dict__[self.field.attname]  # Get the raw PEM from instance dict
            return self.field.to_python(raw_value)  # Convert to WebAuthn CBOR format

        def __set__(self, instance, value):
            # Set the raw value in PEM format
            instance.__dict__[self.field.attname] = value
