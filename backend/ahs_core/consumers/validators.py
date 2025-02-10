import base64
from uuid import UUID

from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.core.exceptions import ValidationError


User = get_user_model()


def is_valid_uuid(socket_url):
    try:
        UUID(socket_url, version=4)
        return True
    except ValueError:
        return False


async def validate_socket_url(socket_url: UUID, user):
    if not socket_url:
        raise ValidationError("socket_url is missing.")

    # Validate format (if UUID)
    if not is_valid_uuid(socket_url):
        raise ValidationError("Invalid socket_url format.")

    # Validate is in database and belongs to user
    enc_socket_url = base64.urlsafe_b64encode(str(socket_url).encode()).decode()
    user_session_key = user.session.session_key

    if not await Session.objects.filter(
        sessionsocketurl__exact=enc_socket_url,
        session_key=user_session_key
    ).aexists():
        raise ValidationError(f"No session matches socket_url {socket_url} & session_key {user_session_key}")
    return True


def validate_ahsuser(ahsuser: User):

    if not ahsuser:
        raise ValidationError("ahsuser is missing.")

    if not isinstance(ahsuser, User):
        raise ValidationError("ahsuser is not an instance of User.")

    if not ahsuser.is_authenticated:
        raise ValidationError("ahsuser is not authenticated.")

    if not ahsuser.has_perm():
        raise ValidationError("ahsuser does not have permission.")
