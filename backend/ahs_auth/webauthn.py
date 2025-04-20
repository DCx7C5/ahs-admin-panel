from django.conf import settings
from webauthn.helpers.cose import COSEAlgorithmIdentifier


PROTOCOL = 'http' if settings.DEBUG else 'https'
PORT = ':8000' if settings.DEBUG else ''

RP_NAME = settings.SITE_NAME
EXPECTED_RP_ID = settings.DOMAIN_NAME
PROTOCOLS = ['http', 'https']  # Allow both protocols in development
EXPECTED_ORIGIN = [f"{proto}://{host}{PORT}" for proto in PROTOCOLS for host in settings.ALLOWED_HOSTS] + [f"{proto}://{host}" for proto in PROTOCOLS for host in settings.ALLOWED_HOSTS]
SUPPORTED_ALGOS = [
    COSEAlgorithmIdentifier.ECDSA_SHA_512,
    COSEAlgorithmIdentifier.ECDSA_SHA_256,
    COSEAlgorithmIdentifier.EDDSA,
    COSEAlgorithmIdentifier.RSASSA_PSS_SHA_512,
]

CREATE_SUPERUSER_JS_CODE = """
Copy and paste the following JS code to your browser's developer console
and input the JSON object here in this prompt:\n\nfunction arrayBufferToBase64Url(buffer) {const binary = String.fromCharCode(...new Uint8Array(buffer));return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');};const enc=new TextEncoder();const dec=new TextDecoder();
const o=JSON.parse('%s');o.user.id=enc.encode(atob(o['user']['id']));o.challenge=enc.encode(atob(o.challenge));
const c=await navigator.credentials.create({ publicKey: o });const sc={id: c.id, rawId: arrayBufferToBase64Url(c.rawId),
response: {clientDataJSON: arrayBufferToBase64Url(c.response.clientDataJSON),attestationObject: arrayBufferToBase64Url(c.response.attestationObject)},
type: "public-key"};console.log(JSON.stringify(sc));\n\nPaste console output: >>>"""