from adrf.serializers import ModelSerializer
from .models import Category, Bookmark


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'name',
            'uuid',
            'id',
            'active',
        )


class BookmarkSerializer(ModelSerializer):
    class Meta:
        model = Bookmark
        fields = (
            'id',
            'name',
            'url',
            'icon_url',
            'uuid',
        )
