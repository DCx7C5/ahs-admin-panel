import logging

from django.contrib.auth import login
from django.contrib.auth.decorators import login_not_required
from django.middleware.csrf import rotate_token
from django.shortcuts import render


logger = logging.getLogger(__name__)


@login_not_required
async def signup_view(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        publicKey = request.POST.get('publicKey')
        rotate_token(request)

    else:
        logger.debug(f"you visited signup")
    return render(request, "base.html", {})


@login_not_required
async def login_view(request):
    context = {}

    response = render(request, "base.html",context)
    return response


async def default_view(request):
    context = {}
    response = render(request, "base.html",context)
    return response
