from abc import ABCMeta

from django.db import models
from django.db.models import JSONField



class DockerVolume(models.Model):
    # Basic volume information
    name = models.CharField(max_length=256, primary_key=True)
    created_at = models.DateTimeField()
    driver = models.CharField(max_length=64)  # e.g., "local"
    mountpoint = models.TextField()  # The path where the volume is mounted
    scope = models.CharField(max_length=64, choices=[("local", "local"), ("global", "global")], default="local")

    # Additional fields
    labels = JSONField(blank=True, null=True)  # Metadata or labels for the volume
    options = JSONField(blank=True, null=True)  # Driver-specific options

    def __str__(self):
        return f"Volume: {self.name} (Driver: {self.driver})"

    class Meta:
        managed = False


class DockerNetwork(models.Model):
    # Basic network information
    name = models.CharField(max_length=256)
    network_id = models.CharField(max_length=256, primary_key=True)
    created = models.DateTimeField()
    scope = models.CharField(max_length=64)  # e.g., "local", "swarm"
    driver = models.CharField(max_length=64)  # e.g., "bridge", "host", "null"
    enable_ipv6 = models.BooleanField(default=False)
    internal = models.BooleanField(default=False)
    attachable = models.BooleanField(default=False)
    ingress = models.BooleanField(default=False)
    config_only = models.BooleanField(default=False)

    # IPAM (IP Address Management)
    ipam_driver = models.CharField(max_length=64, blank=True, null=True)
    ipam_options = JSONField(blank=True, null=True)  # Options related to IPAM
    ipam_config = JSONField(blank=True, null=True)  # List of Subnet/Gateway configurations

    # Configurations related to the network
    config_from = JSONField(blank=True, null=True)  # e.g., {"Network": ""}
    containers = JSONField(blank=True, null=True)  # Details of containers in the network
    options = JSONField(blank=True, null=True)  # Additional options for the driver
    labels = JSONField(blank=True, null=True)  # Metadata such as Compose labels

    def __str__(self):
        return f"Network: {self.name} (Driver: {self.driver})"

    class Meta:
        managed = False


class DockerContainer(models.Model):
    # Basic container information
    container_id = models.CharField(max_length=256, primary_key=True)
    names = JSONField()  # List of container names
    image = models.CharField(max_length=256)
    image_id = models.CharField(max_length=256)
    command = models.TextField()
    created = models.DateTimeField()
    state = models.CharField(max_length=64)  # e.g., "running", "exited"
    status = models.CharField(max_length=256)  # e.g., "Up 3 hours"

    # Ports and network configurations
    ports = JSONField()  # List of port mappings
    labels = JSONField(blank=True, null=True)  # Store container labels as JSON
    network_mode = models.CharField(max_length=256, blank=True, null=True)
    networks = JSONField(blank=True, null=True)  # Store network settings as JSON

    # Mounts (volumes and binds)
    mounts = JSONField(blank=True, null=True)  # Store mount details as JSON

    def __str__(self):
        return f"Docker Container: {self.names[0] if self.names else self.container_id}"

    class Meta:
        managed = False


class DockerImage(models.Model, metaclass=ABCMeta):
    # Basic information
    id = models.CharField(max_length=256, primary_key=True)
    repo_tags = JSONField()
    repo_digests = JSONField()
    parent = models.CharField(max_length=256, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created = models.DateTimeField()
    docker_version = models.CharField(max_length=256, blank=True, null=True)
    author = models.CharField(max_length=256, blank=True, null=True)

    # Config-related fields
    config_hostname = models.CharField(max_length=256, blank=True, null=True)
    config_domainname = models.CharField(max_length=256, blank=True, null=True)
    config_user = models.CharField(max_length=256, blank=True, null=True)
    config_env = JSONField()  # Store environment variables
    config_cmd = JSONField()  # Command to run in the container
    config_entrypoint = JSONField(blank=True, null=True)
    config_labels = JSONField(blank=True, null=True)
    config_working_dir = models.CharField(max_length=512, blank=True, null=True)
    config_volumes = JSONField(blank=True, null=True)

    # OS, architecture, and size
    architecture = models.CharField(max_length=256)
    os = models.CharField(max_length=256)
    size = models.BigIntegerField()

    # Graph driver fields
    graphdriver_name = models.CharField(max_length=256)
    graphdriver_data = JSONField()  # Store data fields such as "LowerDir"

    # RootFS and Layers
    rootfs_type = models.CharField(max_length=256)
    rootfs_layers = JSONField()  # Store the list of layers

    # Metadata
    metadata_last_tag_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Docker Image: {self.repo_tags if self.repo_tags else 'Unknown'}"


    class Meta:
        managed = False


class AHSCompose(models.Model):
    class Meta:
        managed = False