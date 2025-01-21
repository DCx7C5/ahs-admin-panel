from adrf.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from backend.core.models import AHSEndPoint, SessionSocketURL
from backend.core.models.host import Host

AHSUser = get_user_model()


class MenuItemSerializer(ModelSerializer):
    class Meta:
        model = AHSEndPoint
        fields = [
            "name",
            "path",
            "icon",
            "order",
            "active",
            "parent",
        ]

    async def get_children(self, obj):
        children = []
        if await obj.children.aexists():
            async for ch in obj.children.all():
                children.append(ch)
            return await MenuItemSerializer(children, many=True).data
        return []


    async def validate_order(self, value):
        """
        Ensures the order is non-negative.
        """
        if value < 0:
            raise serializers.ValidationError("Order must be a non-negative integer.")
        return value

    async def validate_parent(self, value):
        """
        Custom validation to prevent circular relationships in the parent field.
        """
        if value and self.instance:
            if self.instance == value:
                raise serializers.ValidationError("A menu item cannot be its own parent.")
        return value


class HostSerializer(ModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'


class AHSUserSerializer(ModelSerializer):
    class Meta:
        model = AHSUser
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'is_active', 'is_staff', 'is_superuser',
            'last_login', 'image', 'uid',
        ]

class SessionSocketUrlSerializer(ModelSerializer):
    class Meta:
        model = SessionSocketURL
        fields = ('path',)
