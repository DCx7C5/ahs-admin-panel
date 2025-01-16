import logging

from backend.bookmarks.models import Category, Bookmark
from backend.bookmarks.serializer import CategorySerializer, BookmarkSerializer
from backend.core.consumers.cmd_parser import websocket_cmd

logger = logging.getLogger(__name__)


@websocket_cmd
async def get_bm_categories(user):
    logger.debug(f'get_bm_categories user: {user}')
    async for cat in Category.objects.filter(owner=user.id, active=True).all():
        yield await CategorySerializer(cat).adata


@websocket_cmd
async def get_bookmarks(uuid, user, id):
    logger.debug(f'get_bookmarks user: {user} id: {id}')
    async for bm in Bookmark.objects.filter(owner=user.id, uuid=uuid).all():
        yield await BookmarkSerializer(bm).adata
