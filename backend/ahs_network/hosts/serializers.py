from adrf.serializers import ModelSerializer

from backend.ahs_network.hosts.models import Host


class HostSerializer(ModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'
