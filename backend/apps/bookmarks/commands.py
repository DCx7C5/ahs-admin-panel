import logging
from uuid import UUID

from backend.core.accounts import AHSUser
from backend.apps.bookmarks.models import Category, Bookmark
from backend.apps.bookmarks.serializer import CategorySerializer, BookmarkSerializer
from backend.core.consumers.cmd_parser import websocket_cmd

logger = logging.getLogger(__name__)


@websocket_cmd
async def get_bm_categories(user):
    """
    Fetch all active bookmark categories associated with a specific user.

    This function is an asynchronous WebSocket command that retrieves active
    bookmark categories for a given user, serializes them, and yields the results.

    Args:
        user (:model:`accounts.AHSUser`): The user for whom the categories are being retrieved.

    Yields:
        dict: Serialized bookmark category data using :model:`bookmarks.Category`.

    Related Models and Components:
        - Categories: :model:`bookmarks.Category`
        - Serializer: `CategorySerializer`

    Logging:
        Logs the user making the request for debugging purposes.

    Example Use Case:
        Retrieve and display active bookmark categories for a user in a real-time
        WebSocket application, such as in a frontend category dropdown.
    """
    logger.debug(f'get_bm_categories user: {user}')
    async for cat in Category.objects.filter(owner=user.id, active=True).all():
        yield await CategorySerializer(cat).adata


@websocket_cmd
async def get_bookmarks(uuid: UUID, user: AHSUser, id: int):
    """
    Fetch bookmarks associated with a specific UUID and user.

    This asynchronous WebSocket command retrieves bookmarks owned by a specified
    user and linked with the given UUID. Results are serialized and yielded as an
    asynchronous stream.

    Args:
        uuid (UUID): The universally unique identifier associated with the set of bookmarks.
        user (:model:`accounts.AHSUser`): The user whose bookmarks are being retrieved.
        id (int): An additional identifier (e.g., UI context or API tracking purpose).

    Yields:
        dict: Serialized bookmark data using :model:`bookmarks.Bookmark`.

    Related Models and Components:
        - Bookmarks: :model:`bookmarks.Bookmark`
        - Serializer: `BookmarkSerializer`

    Logging:
        Logs details of the user, UUID, and ID for debugging.

    Example Use Case:
        Retrieves and displays bookmarks from a specified category or other grouping,
        identified using the category UUID provided by the user. For instance, a UI item
        representing a category may trigger this command.
    """
    logger.debug(f'get_bookmarks user: {user} id: {id}')
    async for bm in Bookmark.objects.filter(owner=user.id, uuid=uuid).all():
        yield await BookmarkSerializer(bm).adata
