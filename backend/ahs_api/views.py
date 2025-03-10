import logging

from adrf.views import APIView
from rest_framework.authentication import BaseAuthentication


logger = logging.getLogger(__name__)

class AsyncAuthentication(BaseAuthentication):
    async def authenticate(self, request):
        pass


class SignupView(APIView):
    http_method_names = ['post']

    async def post(self, request):
        username = request.data.get('username')
        public_key = request.data.get('public_key')
        salt = request.data.get('salt')
        logger.debug(f"{username}, {public_key}, {salt}")

class LoginView(APIView):
    async def post(self, request):
        username = request.data.get('username')
        public_key = request.data.get('public_key')


