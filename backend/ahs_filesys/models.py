from django.db.models.fields import SmallIntegerField
from magic import Magic

from django.db.models import (
    BigIntegerField,
    BooleanField,
    ForeignKey,
    JSONField,
    CharField,
    SET_NULL, DateTimeField, TextField, Model,
)
from django.utils.translation import gettext_lazy as _

from backend.ahs_core.fields import NameField
from backend.ahs_core.models import TreeMixin
from backend.ahs_filesys.fields import (
    OctalIntegerField,
    UnixAbsolutePathField,
    MD5HashField,
    SHA256HashField,
)


class UnixFilesystem(Model):
    name = NameField(
        max_length=255,
        unique=True,
        verbose_name=_("Filesystem Name"),
        help_text=_("The name of the UNIX filesystem."),
    )

    host = ForeignKey(
        'ahs_core.Host',
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name='filesystems',
        verbose_name=_("Host"),
        help_text=_("Host where this filesystem resides."),
    )

    class Meta:
        app_label = 'ahs_core'
        ordering = ['name']
        db_table = 'ahs_core_filesys_unixfilesystem'
        verbose_name = _("UNIX Filesystem")
        verbose_name_plural = _("UNIX Filesystems")

    def __str__(self):
        return self.name


class UnixFilePath(Model, TreeMixin):
    name = NameField(
        verbose_name=_("File Name"),
        help_text=_("The base name of the file."),
    )

    permissions = OctalIntegerField(
        verbose_name=_("File Permissions"),
        help_text=_("File permissions in octal format, e.g. 0755."),
    )

    uid = SmallIntegerField(
        blank=False,
        verbose_name=_("User ID"),
        help_text=_("User ID of the file owner."),
    )

    gid = SmallIntegerField(
        blank=False,
        verbose_name=_("Group ID"),
        help_text=_("Group ID of the file owner."),
    )

    path = UnixAbsolutePathField(
        verbose_name=_("File Path"),
        help_text=_("Full or relative file path."),
        unique=True,
    )

    size = BigIntegerField(
        verbose_name=_("Size (bytes)"),
        null=True,
        blank=True,
        help_text=_("Size of the file in bytes."),
    )

    checksum = CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=_("Checksum"),
        help_text=_("File checksum (e.g. SHA256)."),
    )

    is_symlink = BooleanField(
        default=False,
        verbose_name=_("Is Symlink"),
        help_text=_("Is this file a symbolic link?"),
    )

    symlink_target = CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Symlink Target Path"),
        help_text=_("If symlink, the path it links to."),
    )

    tags = JSONField(
        default=list,
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Arbitrary tags or labels for this file."),
    )

    created_at = DateTimeField(
        auto_now_add=True,
        verbose_name=_("Record Created"),
    )

    updated_at = DateTimeField(
        auto_now=True,
        verbose_name=_("Record Modified"),
    )

    last_accessed = DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Accessed"),
    )

    description = TextField(
        blank=True,
        default='',
        verbose_name=_("Description"),
        help_text=_("Optional description or notes about this file."),
    )

    hash_md5 = MD5HashField(
        null=True,
        blank=True,
        verbose_name=_("MD5 Hash"),
        help_text=_("MD5 hash of the file content."),
    )

    hash_sha256 = SHA256HashField(
        null=True,
        blank=True,
        verbose_name=_("SHA256 Hash"),
        help_text=_("SHA256 hash of the file content."),
    )

    class Meta:
        app_label = 'ahs_core'
        unique_together = (('name', 'path'),)
        verbose_name = _("UNIX File")
        verbose_name_plural = _("UNIX Files")
        ordering = ['-updated_at', 'path']
        db_table = 'ahs_core_filesys_unixfile'

    def __str__(self):
        return f"{self.path} ({self.permissions})"

    @property
    def mime_type(self):
        _magic = Magic(mime=True)
        return _magic.from_file(self.path)

    @property
    def file_extension(self):
        # Return the file extension; empty string if no extension.
        return self.name.rsplit(".", 1)[-1] if '.' in self.name else ""

    def has_tag(self, tag):
        return tag in self.tags if self.tags else False

    def add_tag(self, tag):
        if self.tags is None:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
            self.save()
        return self.tags

    def remove_tag(self, tag):
        if self.tags is None:
            return None
        if tag in self.tags:
            self.tags.remove(tag)
            self.save()
        return self.tags

    def get_readable_permissions(self):
        # Converts octal permission to rwx string, e.g. 0o755 -> 'rwxr-xr-x'
        perm = self.permissions
        out = ""
        for who in [(perm >> 6) & 0b111, (perm >> 3) & 0b111, perm & 0b111]:
            out += 'r' if who & 0b100 else '-'
            out += 'w' if who & 0b010 else '-'
            out += 'x' if who & 0b001 else '-'
        return out

    def as_dict(self, include_directory=False):
        # Utility to serialize the file to a dict
        data = {
            "id": self.pk,
            "name": self.name,
            "path": self.path,
            "permissions": self.permissions,
            "permissions_display": self.get_readable_permissions(),
            "uid": self.uid,
            "gid": self.gid,
            "size": self.size,
            "checksum": self.checksum,
            "is_symlink": self.is_symlink,
            "symlink_target": self.symlink_target,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_accessed": self.last_accessed,
            "description": self.description,
            "file_extension": self.file_extension,
        }
        if include_directory:
            data['parent'] = str(self.parent) if self.parent else None

        return data
