from django.contrib import admin
from django.contrib.admin import ModelAdmin

from backend.apps.bookmarks.models import Bookmark, BookmarksProfile


# Register your models here.
@admin.register(Bookmark)
class BookmarkAdmin(ModelAdmin):
    list_display = ('id', 'icon_tag', 'name', 'url', 'created', 'updated', 'owner_id')
    ordering = ('owner_id',)

@admin.register(BookmarksProfile)
class BookmarksProfileAdmin(ModelAdmin):
    list_display = ('id', 'user_id')
