from adrf.serializers import ModelSerializer
from django.contrib.auth import get_user_model


AHSUser = get_user_model()


class AHSUserSerializer(ModelSerializer):
    class Meta:
        model = AHSUser
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'email', 'is_active', 'is_staff', 'is_superuser',
            'last_login', 'image', 'uid',
        ]
