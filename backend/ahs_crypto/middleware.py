import base64

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from django.http import HttpResponse
from django.utils.decorators import async_only_middleware


@async_only_middleware
class ECCAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.server_private_key = ec.generate_private_key(ec.SECP521R1())
        self.server_public_key = self.server_private_key.public_key()

    async def __call__(self, request):
        response = await self.process_request(request)
        if isinstance(response, HttpResponse):
            return response
        return await self.get_response(request)

    @staticmethod
    async def process_request(request):
        # Here we assume the client sends a signature and the challenge in headers
        if 'HTTP_X_CLIENT_SIGNATURE' in request.META and 'HTTP_X_CHALLENGE' in request.META:
            client_signature = base64.b64decode(request.META['HTTP_X_CLIENT_SIGNATURE'])
            challenge = request.META['HTTP_X_CHALLENGE'].encode()

            # Load client's public key from a hypothetical storage method
            # In real-world scenarios, you'd retrieve this from a secure storage
            client_public_key_pem = request.META.get('HTTP_X_CLIENT_PUBLIC_KEY')
            if not client_public_key_pem:
                return HttpResponse("Client public key not provided", status=401)

            client_public_key = serialization.load_pem_public_key(
                client_public_key_pem.encode()
            )

            try:
                # Verify signature
                # Note: verify is not an async method, so we run it in the event loop directly
                client_public_key.verify(client_signature, challenge, ec.ECDSA(hashes.SHA512()))
                # If verification passes, proceed with the request
                request.user = "Authenticated User"  # Placeholder, could be more complex user object
            except InvalidSignature:
                return HttpResponse("Authentication failed", status=401)
        else:
            return HttpResponse("Authentication headers missing", status=401)