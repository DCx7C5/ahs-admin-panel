import logging

from django.conf import settings
from django.contrib.auth.decorators import login_not_required, login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@login_not_required
@require_http_methods(["GET"])
async def login_view(request):

    redirect_to = settings.LOGIN_REDIRECT_URL
    user = await request.auser()

    # Handle already authenticated users
    if user and user.is_authenticated:
        return HttpResponseRedirect(redirect_to)

    return render(request, 'login.html', {})


@csrf_exempt
@login_not_required
@require_http_methods(["GET"])
async def signup_view(request):
    return render(request, 'register.html', {})


@require_http_methods(["GET"])
@login_required(login_url="/accounts/login/")
async def default_view(request):
    return render(request, "base.html", {})
