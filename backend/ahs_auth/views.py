import logging
import secrets
import uuid

from adrf.decorators import api_view

from django.contrib.auth import get_user_model, alogin
from django.core.cache import cache
from django.db.models import QuerySet
from rest_framework.response import Response
from webauthn.helpers import parse_authentication_credential_json
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from webauthn.helpers.exceptions import InvalidAuthenticationResponse, InvalidRegistrationResponse

from webauthn.helpers.options_to_json import options_to_json
from webauthn.helpers.structs import (
    PublicKeyCredentialCreationOptions,
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    AuthenticatorAttachment,
    UserVerificationRequirement,
    ResidentKeyRequirement,
    PublicKeyCredentialDescriptor,
)

from webauthn.registration.verify_registration_response import verify_registration_response, VerifiedRegistration
from webauthn.registration.generate_registration_options import generate_registration_options
from webauthn.authentication.generate_authentication_options import generate_authentication_options
from webauthn.authentication.verify_authentication_response import verify_authentication_response, \
    VerifiedAuthentication

from backend.ahs_auth.models import WebAuthnCredential, AuthMethod
from backend.ahs_auth.webauthn import EXPECTED_RP_ID, EXPECTED_ORIGIN, SUPPORTED_ALGOS
from backend.ahs_core.utils import aencode_b64
from config import settings

logger = logging.getLogger(__name__)

User = get_user_model()

REGISTRATION_ERROR = "Registration error. Please try again." if not settings.DEBUG else "Registration error: {}"
AUTHENTICATION_ERROR = "Authentication error. Please try again." if not settings.DEBUG else "Authentication error: {}"


@api_view(['POST'])
async def webauthn_register_view(request):
    data = request.data

    try:
        username = data.get('username')
        user_pubkey_cred_params = data.get('pubkeycredparams')
        user_auth_attachment = data.get('authattachment')
    except Exception as e:
        return Response(
            {"errors": REGISTRATION_ERROR.format(e)},
            status=400,
        )

    if not all([username, user_pubkey_cred_params, user_auth_attachment]):
        return Response(
            {"errors": REGISTRATION_ERROR},
            status=400,
        )

    user_query = User.objects.filter(username=username)
    if await user_query.aexists() and not (await user_query.aget()).is_superuser:
        return Response(
            {"errors": "Registration error. Username already exists. Please try again."},
            status=400,
        )

    challenge = secrets.token_bytes(128).hex()
    user_id = f"{uuid.uuid4()}"
    random = secrets.token_hex(32)

    options: PublicKeyCredentialCreationOptions = generate_registration_options(
        rp_name=settings.SITE_NAME,
        rp_id=request.get_host(),
        user_id=user_id.encode('utf-8'),
        user_name=username,
        user_display_name=username,
        challenge=challenge.encode('utf-8'),
        timeout=180,
        exclude_credentials=[],
        supported_pub_key_algs=[COSEAlgorithmIdentifier(p) for p in user_pubkey_cred_params],
        attestation=AttestationConveyancePreference.NONE,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.PREFERRED,
            authenticator_attachment=AuthenticatorAttachment(user_auth_attachment),
            user_verification=UserVerificationRequirement.PREFERRED,
        ),
    )

    json_options = options_to_json(options=options)

    await cache.aset(f"{random}", f"{challenge}.|.{username}.|.{user_id}", 180)
    print(challenge, username, user_id, random, options, json_options, sep="|")
    return Response(
        {
            "message": "Generated registration options successfully.",
            "options": json_options,
            "random": random,
        },
        status=200,
    )


@api_view(['POST'])
async def webauthn_verify_registration_view(request):
    data = request.data
    json_cred = data.get("credential")
    random = data.get("random", None)
    cached_value = await cache.aget(random, None)
    await cache.adelete(random)

    if not json_cred or not random:
        return Response(
            {"errors": REGISTRATION_ERROR},
            status=400,
        )

    if not cached_value:
        return Response(
            {"errors": "Registration timed out. Please try again."},
            status=400,
        )

    challenge, username, user_id = cached_value.split('.|.')

    try:
        verified_registration: VerifiedRegistration = verify_registration_response(
            credential=json_cred,
            expected_challenge=challenge.encode('utf-8'),
            expected_rp_id=request.get_host(),
            expected_origin=EXPECTED_ORIGIN,
            supported_pub_key_algs=SUPPORTED_ALGOS,
        )
    except InvalidRegistrationResponse as e:
        return Response(
            {"errors": REGISTRATION_ERROR},
            status=400,
        )

    new_user, created = await User.objects.aget_or_create(username=username)

    if created:
        new_user.uid = user_id
        await new_user.asave()

    auth_method = await AuthMethod.objects.filter(name="webauthn").aget()

    await new_user.available_auth.aadd(auth_method)

    await new_user.webauthn_credentials.acreate(
        credential_id=await aencode_b64(verified_registration.credential_id, safe=True),
        public_key=verified_registration.credential_public_key,
        credential_type=verified_registration.credential_type.value,
        device_type=verified_registration.credential_device_type.value,
        sign_count=verified_registration.sign_count,
    )

    return Response(
        {
            "message": "Registration successful.",
            "status": 200,
        },
        status=200,
    )



@api_view(['POST'])
async def webauthn_authentication_view(request):
    data = request.data
    username = data.get("username")

    challenge = secrets.token_hex(64)
    random = secrets.token_hex(64)

    cids_qs: QuerySet = WebAuthnCredential.objects.filter(
        user__username=username,
    ).values_list(
        'credential_id',
        'credential_type',
    )

    if not await cids_qs.aexists():
        return Response(
            {"errors": "Authentication error. No credentials found for this user. Please try again."},
            status=400,
        )

    options = generate_authentication_options(
        rp_id=EXPECTED_RP_ID,
        challenge=challenge.encode('utf-8'),
        timeout=180,
        user_verification=UserVerificationRequirement.PREFERRED,
        allow_credentials=[
            PublicKeyCredentialDescriptor(*cids) async for cids in cids_qs
        ],
    )

    await cache.aset(f"{random}", f"{challenge}", 180)

    json_options = options_to_json(options=options)

    return Response(
        {
            "message": "Generated authentication options successfully.",
            "options": json_options,
            "random": random,
        },
        status=200,
    )


@api_view(['POST'])
async def webauthn_verify_authentication_view(request):
    data = request.data
    json_auth_cred = data.get("credential")
    random = data.get("random")
    username = data.get("username")
    auth_cred = parse_authentication_credential_json(json_auth_cred)

    cached_challenge = await cache.aget(random, None)
    if not cached_challenge:
        return Response(
            {"errors": "Authentication timed out. Please try again."},
            status=400
        )
    await cache.adelete(random)

    user = await User.objects.aget(username=username)

    if not user:
        return Response(
            {"errors": AUTHENTICATION_ERROR},
            status=400
        )

    db_cred: WebAuthnCredential = await user.webauthn_credentials.aget(
        credential_id=auth_cred.id
    )

    try:
        verified_auth: VerifiedAuthentication = verify_authentication_response(
            credential=json_auth_cred,
            expected_challenge=cached_challenge.encode('utf-8'),
            expected_rp_id=EXPECTED_RP_ID,
            expected_origin=EXPECTED_ORIGIN,
            require_user_verification=True,
            credential_public_key=db_cred.public_key,
            credential_current_sign_count=db_cred.sign_count,
        )
    except InvalidAuthenticationResponse as e:
        return Response(
            {"errors": AUTHENTICATION_ERROR.format(e)},
            status=400
        )

    db_cred.sign_count = verified_auth.new_sign_count
    await db_cred.asave()

    await alogin(request, user)

    return Response(
        {"message": "Authentication successful."},
        status=200,
    )
