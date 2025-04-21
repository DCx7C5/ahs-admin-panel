import logging
import secrets
import uuid

from adrf.decorators import api_view
from django.contrib.auth import get_user_model, alogin
from django.core.cache import cache
from rest_framework.response import Response
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.exceptions import InvalidAuthenticationResponse, InvalidRegistrationResponse

from webauthn.helpers.options_to_json import options_to_json
from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    AuthenticatorAttachment,
    PublicKeyCredentialHint,
    UserVerificationRequirement,
    PublicKeyCredentialDescriptor,
)
from webauthn.registration.verify_registration_response import verify_registration_response, VerifiedRegistration
from webauthn.registration.generate_registration_options import generate_registration_options
from webauthn.authentication.generate_authentication_options import generate_authentication_options
from webauthn.authentication.verify_authentication_response import verify_authentication_response, \
    VerifiedAuthentication

from backend.ahs_auth.models import WebAuthnCredential
from backend.ahs_auth.webauthn import EXPECTED_RP_ID, EXPECTED_ORIGIN, SUPPORTED_ALGOS
from backend.ahs_core.utils import adecode_json
from config import settings

logger = logging.getLogger(__name__)

User = get_user_model()

REGISTRATION_ERROR = "Registration error. Please try again." if not settings.DEBUG else "{}"
AUTHENTICATION_ERROR = "Authentication error. Please try again." if not settings.DEBUG else "{}"


@api_view(['POST'])
async def webauthn_register_view(request):
    data = request.data
    j_username = data.get("username")
    j_publickey = data.get("pubkeycredparams")
    j_auth_attachment = data.get("authattachment")

    if not all([j_username, j_publickey, j_auth_attachment]):
        return Response(
            {"errors": REGISTRATION_ERROR},
            status=400,
        )

    try:
        username = await adecode_json(j_username)
        user_pubkey_cred_params = await adecode_json(j_publickey)
        user_auth_attachment = await adecode_json(j_auth_attachment)
    except Exception as e:
        return Response(
            {"errors": REGISTRATION_ERROR.format(e)},
            status=400,
        )

    if await User.objects.filter(username=username).aexists():
        return Response(
            {"errors": "Registration error. Username already exists. Please try again."},
        )

    challenge = secrets.token_bytes(128).hex()
    user_id = f"{uuid.uuid4()}"
    random = secrets.token_hex(32)

    options: PublicKeyCredentialCreationOptions = generate_registration_options(
        rp_name=settings.SITE_NAME,
        rp_id=EXPECTED_RP_ID,
        user_id=user_id.encode('utf-8'),
        user_name=username,
        user_display_name=username,
        challenge=challenge.encode('utf-8'),
        timeout=60000,
        supported_pub_key_algs=[COSEAlgorithmIdentifier(p) for p in user_pubkey_cred_params],
        attestation=AttestationConveyancePreference.DIRECT,
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment=AuthenticatorAttachment(user_auth_attachment),
            user_verification=UserVerificationRequirement.REQUIRED,
        ),
        hints=[
            PublicKeyCredentialHint.SECURITY_KEY,
            PublicKeyCredentialHint.CLIENT_DEVICE,
            PublicKeyCredentialHint.HYBRID,
        ]
    )

    json_options = options_to_json(options=options)

    await cache.aset(f"{random}", f"{challenge}.|.{username}.|.{user_id}", 600)

    return Response(
        {
            "message": "Generated registration options.",
            "options": json_options,
            "random": random,
        },
        status=200,
    )


@api_view(['POST'])
async def webauthn_verify_registration_view(request):
    data = request.data
    json_cred = data.get("credential", None)
    random = data.get("random", None)
    cached_value = await cache.aget(random, None)

    if not cached_value:
        return Response(
            {"errors": "Registration timed out. Please try again."},
            status=400,
        )

    if not json_cred or not random:
        return Response(
            {"errors": "Registration error. Please try again."},
            status=400,
        )


    await cache.adelete(random)

    challenge, username, user_id = cached_value.split('.|.')
    try:
        verified_registration: VerifiedRegistration = verify_registration_response(
            credential=json_cred,
            expected_challenge=challenge.encode('utf-8'),
            expected_rp_id=EXPECTED_RP_ID,
            expected_origin=EXPECTED_ORIGIN,
            supported_pub_key_algs=SUPPORTED_ALGOS,
        )
    except InvalidRegistrationResponse as e:
        return Response(
            {"errors": REGISTRATION_ERROR.format(e)},
            status=400
        )

    new_user = await User.objects.acreate(
        username=username,
        uid=user_id,
    )

    new_creds = await WebAuthnCredential.objects.acreate(
        user=new_user,
        credential_id=verified_registration.credential_id.decode('utf-8'),
        public_key=verified_registration.credential_public_key.decode('utf-8'),
        credential_type=verified_registration.credential_type,
        device_type=verified_registration.credential_device_type,
        sign_count=verified_registration.sign_count,
    )

    await new_user.asave()
    await new_creds.asave()

    return Response(
        {
            "message": "Registration successful.",
        },
        status=200,
    )



@api_view(['POST'])
async def webauthn_authentication_view(request):
    data = request.data

    try:
        username = await adecode_json(data.get("username"))
    except Exception as e:
        return Response(
            {"errors": AUTHENTICATION_ERROR.format(e)},
            status=400
        )

    challenge = secrets.token_hex(64)
    random = secrets.token_hex(64)

    options = generate_authentication_options(
        rp_id=EXPECTED_RP_ID,
        challenge=challenge.encode('utf-8'),
        timeout=60000,
        user_verification=UserVerificationRequirement.PREFERRED,
    )

    await cache.aset(f"{random}", f"{challenge}.|.{username}", 600)

    json_options = options_to_json(options=options)

    return Response(
        {
            "message": "Authentication successful.",
            "options": json_options,
            "random": random,
        },
        status=200,
    )


@api_view(['POST'])
async def webauthn_verify_authentication_view(request):
    data = request.data
    json_cred = data.get("credential")
    random = data.get("random")

    cached_value = await cache.aget(random, None)
    if not cached_value:
        return Response(
            {"errors": "Authentication timed out. Please try again."},
            status=400
        )

    await cache.adelete(random)

    challenge, username = cached_value.split('.|.')

    user = await User.objects.aget(username=username)

    if not user:
        return Response(
            {"errors": AUTHENTICATION_ERROR},
            status=400
        )

    try:
        verified_auth: VerifiedAuthentication = verify_authentication_response(
            credential=json_cred,
            expected_challenge=challenge.encode('utf-8'),
            expected_rp_id=EXPECTED_RP_ID,
            expected_origin=EXPECTED_ORIGIN,
            require_user_verification=True,
            credential_public_key=None,
            credential_current_sign_count=None,
        )
    except InvalidAuthenticationResponse as e:
        return Response(
            {"errors": AUTHENTICATION_ERROR.format(e)},
            status=400
        )

    print("VERIFIED_AUTH",verified_auth)


    return Response(
        {"message": "Authentication successful."},
        status=200,
    )
