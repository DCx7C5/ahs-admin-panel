from rest_framework.serializers import DateTimeField, IntegerField
from adrf.serializers import ModelSerializer, Serializer
from django.contrib.auth import get_user_model


User = get_user_model()


class AHSUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'is_active', 'is_staff', 'is_superuser',
            'last_login', 'image', 'uid',
        ]


class TokenHeaderSerializer(Serializer):
    token_id = IntegerField()
    created = DateTimeField()
    expired = DateTimeField()

    class Meta:
        fields = ['token_id', 'created', 'expired']


class TokenPayloadSerializer(Serializer):
    """
    Serializer for the token payload
    """

    class Meta:
        fields = ['user', 'session_key', 'session_token']



class TokenSerializer(Serializer):
    """
    Serializer for the token
    """

    header = TokenHeaderSerializer()
    payload = TokenPayloadSerializer()


    class Meta:
        fields = ['header', 'payload']