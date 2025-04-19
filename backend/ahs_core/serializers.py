from rest_framework.serializers import DateTimeField
from adrf.serializers import Serializer




class TokenHeaderSerializer(Serializer):
    created = DateTimeField()
    expires = DateTimeField()

    class Meta:
        fields = ['created', 'expires']



class TokenSerializer(Serializer):
    """
    Serializer for the token
    """

    header = TokenHeaderSerializer()

    class Meta:
        fields = ['header', 'payload']


