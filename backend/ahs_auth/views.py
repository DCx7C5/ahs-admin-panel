import json
import logging
import secrets
import uuid

from adrf.decorators import api_view
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.http import HttpRequest
from rest_framework.response import Response
from webauthn.helpers.options_to_json import options_to_json
from webauthn.helpers.structs import PublicKeyCredentialCreationOptions
from webauthn.registration.verify_registration_response import verify_registration_response
from webauthn.registration.generate_registration_options import generate_registration_options, generate_challenge

from backend.ahs_auth.serializers import LoginSerializer
from backend.ahs_auth.webauthn import EXPECTED_RP_ID, EXPECTED_ORIGIN, SUPPORTED_ALGOS
from config import settings

logger = logging.getLogger(__name__)

User = get_user_model()



@api_view(['POST'])
async def webauthn_register_view(request):
    data = request.data
    username = data.get("username")
    user_pubkey_cred_params = data.get("pubkeycredparams")
    user_auth_attachment = data.get("authattachment")

    print(username)
    print(user_pubkey_cred_params)
    print(user_auth_attachment)

    challenge = generate_challenge()
    rp_name = settings.SITE_NAME
    rp_id = "localhost" if settings.DEBUG else request.get_host()
    user_id = f"{uuid.uuid4()}"
    random = secrets.token_hex(32)

    options: PublicKeyCredentialCreationOptions = generate_registration_options(
        rp_name=settings.SITE_NAME,
        rp_id="localhost" if settings.DEBUG else request.get_host(),
        user_id=user_id.encode('utf-8'),
        user_name=username,
        user_display_name=username,
        challenge=challenge,
        supported_pub_key_algs=user_pubkey_cred_params,
        authenticator_selection=user_auth_attachment,
    )
    print("OPTIONS", options)
    json_options = options_to_json(options=options)
    print("JSON OPTIONS", json_options)

    await cache.aset(f"{random}", f"{challenge.decode('utf-8')}.|.{rp_id}.|.{rp_name}.|.{username}", 600)

    return Response(
        {
            "message": "Generated registration options.",
            "options": json_options,
            "random": random,
        },
        status=200,
    )


@api_view(['POST'])
async def webauthn_verify_view(request):
    data = request.data
    json_creds = data.get("credentials")
    random = data.get("random")

    cached_value = await cache.aget(random, None)
    if not cached_value:
        return Response(
            {"errors": "Registration error. Please try again."},
            status=400
        )

    challenge, rp_id, rp_name, username = cached_value.split('.|.')

    verified_registration = verify_registration_response(
        credential=json_creds,
        expected_challenge=challenge.encode('utf-8'),
        expected_rp_id=EXPECTED_RP_ID,
        expected_origin=EXPECTED_ORIGIN,
        supported_pub_key_algs=SUPPORTED_ALGOS,
    )

    print("VERIFIED_REGISTRATION",verified_registration)







@api_view(['POST'])
async def webauthn_authentication_view(request: HttpRequest):
    serializer = LoginSerializer(data=request.POST)

    if not serializer.is_valid():
        return Response(
            {"errors": serializer.errors},
            status=400
        )

