import logging

from django.contrib.auth import login
from django.contrib.auth.decorators import login_not_required
from django.middleware.csrf import rotate_token
from django.shortcuts import render


logger = logging.getLogger(__name__)

@login_not_required
async def default_view(request):

    is_authenticated = request.user.is_authenticated if hasattr(request, 'user') else False

    initial_data = {
        'isAuthenticated': is_authenticated,
        'publicKey': "TEST",
    }
    if is_authenticated:
        initial_data['user'] = {
            'username': request.user.username,
            'isSuperUser': request.user.is_superuser,
        }

    return render(request, "base.html", initial_data)
