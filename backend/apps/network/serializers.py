from adrf.serializers import ModelSerializer

from backend.apps.network.models.hosts import Host


class HostSerializer(ModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'
