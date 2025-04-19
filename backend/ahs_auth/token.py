import base64
import dataclasses
import logging
from dataclasses import field
from enum import Enum

from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser

from rest_framework.utils.encoders import JSONEncoder
from typing_extensions import NamedTuple, Dict, Union, Optional

from backend.ahs_core.serializers import TokenHeaderSerializer

json_encode = JSONEncoder().encode
header_serializer = TokenHeaderSerializer
logger = logging.getLogger(__name__)
User = get_user_model()

class TokenType(Enum):
    DEFAULT = 0
    AUTH = 1


class TokenHeader:
    __slots__ = ('errors', 'algo',)
    serializer = TokenHeaderSerializer

    async def aencode(self):
        return await self.serializer(self).adata

    def __repr__(self):
        return f"<TokenHeader created={self.created} expires={self.expires}>"


class TokenPayload:
    __slots__ = ('errors', 'payload', '_payload')
    serializer = TokenHeaderSerializer

    async def aencode(self):
        return await self.serializer(self).adata

class TokenSignature:
    __slots__ = ('signature', '_signature', 'errors')




class AHSToken:
    __slots__ = ('header', 'payload', 'signature', '_errors', '_token',
                 '_header', '_payload', '_signature')

    @property
    def user(self):
        return self.payload.user

    async def auser(self):
        return self.payload.auser

    @property
    def id(self):
        return self.header.token_id

    @property
    def created(self):
        return self.header.created

    @property
    def expires(self):
        return self.header.expires

    def is_valid(self) -> bool:
        return len(self._errors) == 0

    async def _encrypt_payload(self, payload):
        """Encrypt the payload with a secret key"""
        return

    async def _decrypt_payload(self, payload):
        """Decrypt the payload with a secret key"""
        return payload

    async def asign(self, ):
        pass

    async def averify(self):
        pass

    @classmethod
    async def afrom_request(cls, token: str = None) -> Optional["AHSToken"]:
        """
        Create an instance of AHSSessionToken from a token string.
        """
        errors = []
        if not token:
            return None

        try:
            h, p, s = token.split('.')
        except ValueError as e:
            logging.getLogger("django.security.SuspiciousSession").warning(
                'Possible token manipulation detected. ' + f'{e}')
            return None


        # Decode the token
        try:
            signature = await TokenSignature.decode_and_validate(s, f"{h}.{p}")
            header = await TokenHeader.decode(h)
            payload = await TokenPayload.decode(p)
        except Exception as e:
            errors.append(f"Error during token instantiation, AHSSessionToken: {e}")
            return None

        errors = header.errors + payload.errors + signature.errors

        if errors:
            logging.getLogger("django.security.SuspiciousSession").warning(
                'Possible token manipulation detected. ' + ' '.join(errors)
            )
            return None

        # Create an instance of AHSSessionToken
        inst = cls()
        inst._token = token
        inst.header = header
        inst.payload = payload
        inst.signature = signature
        return inst

    def __str__(self):
        return self._token

    @classmethod
    async def acreate(cls, user: AbstractBaseUser, token_id: str = None):
        inst = cls()
        inst.header = await TokenHeader.acreate()
        inst.payload = await TokenPayload.acreate()
        inst.signature = await TokenSignature.acreate()

    async def to_string(self):
        return f"{self.header}"