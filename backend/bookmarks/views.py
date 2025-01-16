import logging

from adrf.views import APIView
from django.contrib.auth import aget_user
from django.http import HttpRequest
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

from backend.bookmarks.models import Category

logger = logging.getLogger(__name__)


# Create your views here.
class BookmarksView(APIView):
    permission_classes = [IsAuthenticated]
    view_is_async = True

    async def post(self):
        logger.debug(f'AsyncView: {self.view_is_async}, permission_classes: {self.permission_classes}')


class BookmarksCategoryView(APIView):
    permission_classes = [IsAuthenticated]
    view_is_async = True

    async def post(self, request: HttpRequest):
        logger.debug(f'AsyncView: {self.view_is_async}, permission_classes: {self.permission_classes}')
        user = await aget_user(request)
        bm_cat = await Category.objects.filter(owner=user)
