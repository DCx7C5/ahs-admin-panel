from adrf.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from backend.ahs_endpoints.models import EndPoint

User = get_user_model()


class EndPointSerializer(ModelSerializer):
    class Meta:
        model = EndPoint
        fields = '__all__'

    async def get_children(self, obj):
        children = []
        if await obj.children.aexists():
            async for ch in obj.children.all():
                children.append(ch)
            return await EndPointSerializer(children, many=True).data
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
