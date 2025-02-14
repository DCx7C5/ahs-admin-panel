from django.utils.decorators import async_only_middleware
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser
from django.utils.functional import SimpleLazyObject


async def get_user_from_token(request):
    """
    Decodes the JWT token and authenticates the user.
    """
    try:
        user, _ = JWTAuthentication().authenticate(request)
        return user
    except Exception as e:
        return AnonymousUser()

@async_only_middleware
class JWTAdminAuthMiddleware:
    """
    Custom middleware to add JWT-based authentication for admin.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    async def __call__(self, request):
        # Add `request.user` using JWTAuthentication if token exists
        request.user = SimpleLazyObject(lambda: get_user_from_token(request))
        return self.get_response(request)