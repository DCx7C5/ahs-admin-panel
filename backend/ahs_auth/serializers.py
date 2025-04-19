import logging

from adrf.serializers import Serializer, ModelSerializer
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from backend.ahs_auth.validators import AHSNameValidator, PublicKeyValidator

logger = logging.getLogger(__name__)

User = get_user_model()




class AHSUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser',
            'last_login', 'image', 'uid', 'socket_url', 'public_key'
        ]



class SignupSerializer(Serializer):
    username = serializers.CharField(
        write_only=True,
        help_text="Enter your username.",
        validators=(AHSNameValidator,)
    )
    publickey = serializers.CharField(
        write_only=True,
        help_text="Enter your publickey.",
        validators=(PublicKeyValidator, )
    )
    challenge = serializers.CharField(
        write_only=True,
        help_text="Enter the challenge."
    )

    async def acreate(self, validated_data):
        """
        Asynchronously creates a new user instance.
        """
        try:
            # Hash the public key (password)
            hashed_key = make_password(validated_data["publickey"])

            # Create the new user asynchronously
            new_user = await User.objects.acreate(
                username=validated_data["username"],
                publickey=hashed_key,
            )

            # Log success and return the created user
            logger.info(f"User created successfully: {new_user}")
            return new_user

        except Exception as e:
            # Log and raise error for higher-level handling
            logger.error(f"Error creating user: {e}")
            raise serializers.ValidationError(
                {"error": "An error occurred while creating the user."}
            )

    async def asave(self):
        """
        Saves the validated data and returns the created user instance.
        """
        validated_data = self.validated_data
        return await self.acreate(validated_data)

    class Meta:
        fields = ('username', 'publickey')


class LoginSerializer(Serializer):
    username = serializers.CharField(
        write_only=True,
        help_text="Enter your username."
    )
    public_key = serializers.CharField(
        write_only=True,
        help_text="Enter your password."
    )

