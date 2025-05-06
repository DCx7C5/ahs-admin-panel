from django.db.models import JSONField, CharField, DateTimeField, BigIntegerField, TextField, Model, BooleanField


class DockerVolume(Model):
    # Basic volume information
    name = CharField(max_length=256, primary_key=True)
    created_at = DateTimeField()
    driver = CharField(max_length=64)  # e.g., "local"
    mountpoint = TextField()  # The path where the volume is mounted
    scope = CharField(max_length=64, choices=[("local", "local"), ("global", "global")], default="local")

    # Additional fields
    labels = JSONField(blank=True, null=True)  # Metadata or labels for the volume
    options = JSONField(blank=True, null=True)  # Driver-specific options

    def __str__(self):
        return f"Volume: {self.name} (Driver: {self.driver})"

    class Meta:
        managed = False


class DockerNetwork(Model):
    # Basic ahs_network information
    name = CharField(max_length=256)
    network_id = CharField(max_length=256, primary_key=True)
    created = DateTimeField()
    scope = CharField(max_length=64)  # e.g., "local", "swarm"
    driver = CharField(max_length=64)  # e.g., "bridge", "host", "null"
    enable_ipv6 = BooleanField(default=False)
    internal = BooleanField(default=False)
    attachable = BooleanField(default=False)
    ingress = BooleanField(default=False)
    config_only = BooleanField(default=False)

    # IPAM (IP Address Management)
    ipam_driver = CharField(max_length=64, blank=True, null=True)
    ipam_options = JSONField(blank=True, null=True)  # Options related to IPAM
    ipam_config = JSONField(blank=True, null=True)  # List of Subnet/Gateway configurations

    # Configurations related to the ahs_network
    config_from = JSONField(blank=True, null=True)  # e.g., {"Network": ""}
    containers = JSONField(blank=True, null=True)  # Details of containers in the ahs_network
    options = JSONField(blank=True, null=True)  # Additional options for the driver
    labels = JSONField(blank=True, null=True)  # Metadata such as Compose labels

    def __str__(self):
        return f"Network: {self.name} (Driver: {self.driver})"

    class Meta:
        managed = False


class DockerContainer(Model):
    # Basic container information
    container_id = CharField(max_length=256, primary_key=True)
    names = JSONField()  # List of container names
    image = CharField(max_length=256)
    image_id = CharField(max_length=256)
    command = TextField()
    created = DateTimeField()
    state = CharField(max_length=64)  # e.g., "running", "exited"
    status = CharField(max_length=256)  # e.g., "Up 3 hours"

    # Ports and ahs_network configurations
    ports = JSONField()  # List of port mappings
    labels = JSONField(blank=True, null=True)  # Store container labels as JSON
    network_mode = CharField(max_length=256, blank=True, null=True)
    networks = JSONField(blank=True, null=True)  # Store ahs_network ahs_settings as JSON

    # Mounts (volumes and binds)
    mounts = JSONField(blank=True, null=True)  # Store mount details as JSON

    def __str__(self):
        return f"Docker Container: {self.names[0] if self.names else self.container_id}"

    class Meta:
        managed = False


class DockerImage(Model):
    # Basic information
    id = CharField(max_length=256, primary_key=True)
    repo_tags = JSONField()
    repo_digests = JSONField()
    parent = CharField(max_length=256, blank=True, null=True)
    comment = TextField(blank=True, null=True)
    created = DateTimeField()
    docker_version = CharField(max_length=256, blank=True, null=True)
    author = CharField(max_length=256, blank=True, null=True)

    # Config-related fields
    config_hostname = CharField(max_length=256, blank=True, null=True)
    config_domainname = CharField(max_length=256, blank=True, null=True)
    config_user = CharField(max_length=256, blank=True, null=True)
    config_env = JSONField()  # Store environment variables
    config_cmd = JSONField()  # Command to run in the container
    config_entrypoint = JSONField(blank=True, null=True)
    config_labels = JSONField(blank=True, null=True)
    config_working_dir = CharField(max_length=512, blank=True, null=True)
    config_volumes = JSONField(blank=True, null=True)

    # OS, architecture, and size
    architecture = CharField(max_length=256)
    os = CharField(max_length=256)
    size = BigIntegerField()

    # Graph driver fields
    graphdriver_name = CharField(max_length=256)
    graphdriver_data = JSONField()  # Store data fields such as "LowerDir"

    # RootFS and Layers
    rootfs_type = CharField(max_length=256)
    rootfs_layers = JSONField()  # Store the list of layers

    # Metadata
    metadata_last_tag_time = DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Docker Image: {self.repo_tags if self.repo_tags else 'Unknown'}"


    class Meta:
        managed = False


class AHSCompose(Model):
    class Meta:
        managed = False
