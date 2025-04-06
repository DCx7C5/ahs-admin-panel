import asyncio
import logging
import secrets

from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import login, alogin
from django.contrib.auth.decorators import login_not_required, login_required
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpRequest
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.contrib.auth import login as auth_login
from django.views.decorators.http import require_http_methods

from backend.ahs_core import crypto
from backend.ahs_core.crypto import get_server_public_key

logger = logging.getLogger(__name__)


@login_not_required
@require_http_methods(["GET", "POST"])
async def login_view(request):
    """
    Async implementation of Django's LoginView
    """
    redirect_to = settings.LOGIN_REDIRECT_URL
    user = await request.auser()

    # Handle already authenticated users
    if user and user.is_authenticated:
        return HttpResponseRedirect(redirect_to)

    challenge = await crypto.acreate_login_challenge()

    context = {
        'public_key': f"{crypto.get_server_public_key()}",
        'challenge': challenge,
    }

    return render(request, 'login.html', context)


@login_not_required
@require_http_methods(["GET", "POST"])
async def signup_view(request):
    """
    Async implementation of Django's LoginView
    """
    nonce = secrets.token_urlsafe(32)
    salt = secrets.token_urlsafe(48)

    await cache.aset_many({nonce: True, salt: True}, timeout=300)

    context = {
        'public_key': f"{crypto.get_server_public_key()}",
        'random_str': salt,
    }

    return render(request, 'signup.html', context)


@require_http_methods(["GET", "POST"])
@login_required(login_url="/accounts/login/")
async def default_view(request):
    return render(request, "base.html", {})
