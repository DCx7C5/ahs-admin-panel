import hashlib
from os import PathLike
import os.path as ospath
from os import stat, readlink
from typing import AsyncGenerator

from aiofiles import os as aos
from aiofiles import ospath as aospath
from aiofiles import open as aopen_file
from aiofiles.threadpool.binary import AsyncBufferedReader

from django.db.models.fields import SmallIntegerField
from magic import Magic

from django.db.models import (
    BigIntegerField,
    BooleanField,
    ForeignKey,
    CharField,
    SET_NULL, DateTimeField, TextField, Model, Manager,
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
from backend.ahs_network.hosts.models import Host


async def aread_chunks(file: AsyncBufferedReader, chunk_size: int = 1024) -> AsyncGenerator[bytes, None]:
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        yield chunk


async def aread_file(file: PathLike, cs=1024):
    b = b''
    async with aopen_file(file, 'rb') as f:
        async for chunk in aread_chunks(f, cs):
            b += chunk
    return b


async def awrite_chunks(file: PathLike, chunks: list[bytes]):
    async with aopen_file(file, 'wb') as f:
        for chunk in chunks:
            await f.write(chunk)
            await f.flush()





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


class UnixPathManager(Manager):
    def create_local_path_reference(self, path: PathLike, host: str = "localhost", description: str = None) -> 'UnixFileSystemPath':
        path_abs = ospath.abspath(path)
        path_exists = ospath.exists(path_abs)
        if not path_exists:
            raise FileNotFoundError(f"Path does not exist: {path_abs}")

        is_symlink = ospath.islink(path_abs)

        if path_exists and not is_symlink:
            with open(path_abs, 'rb') as f:
                md5sum = hashlib.md5(f.read()).hexdigest()
                sha256sum = hashlib.sha256(f.read()).hexdigest()

        return self.create(
            path=path_abs,
            permissions=oct(stat(path_abs).st_mode)[-4:],
            uid=stat(path_abs).st_uid,
            gid=stat(path_abs).st_gid,
            size=stat(path_abs).st_size,
            host=Host.objects.get(name='localhost'),
            is_symlink=is_symlink,
            symlink_target=readlink(path_abs) if is_symlink else None,
            created=stat(path_abs).st_ctime,
            modified=stat(path_abs).st_mtime,
            last_accessed=stat(path_abs).st_atime,
            hash_md5=md5sum if not is_symlink else None,
            hash_sha256=sha256sum if not is_symlink else None,
            description=description,
        )

    async def acreate_local_path_reference(self, path: PathLike, host: str = 'localhost', description: str = None) -> 'UnixFileSystemPath':
        path_abs = await aospath.abspath(path)
        path_exists = await aos.path.exists(path_abs)

        if not path_exists:
            raise FileNotFoundError(f"Path does not exist: {path_abs}")

        is_symlink = await aos.path.islink(path_abs)

        if path_exists and not is_symlink:
            async with aopen_file(path_abs, 'rb') as f:
                md5sum = hashlib.md5(await f.read()).hexdigest()
                sha256sum = hashlib.sha256(await f.read()).hexdigest()

        return await self.acreate(
            path=path_abs,
            permissions=oct((await aos.stat(path_abs)).st_mode)[-4:],
            uid=(await aos.stat(path_abs)).st_uid,
            gid=(await aos.stat(path_abs)).st_gid,
            host=await Host.objects.aget(name=host),
            is_symlink=is_symlink,
            symlink_target=(await aos.readlink(path_abs)) if is_symlink else None,
            created=(await aos.stat(path_abs)).st_ctime,
            modified=(await aos.stat(path_abs)).st_mtime,
            last_accessed=(await aos.stat(path_abs)).st_atime,
            hash_md5=md5sum if not is_symlink else None,
            hash_sha256=sha256sum if not is_symlink else None,
            description=description,
        )


class UnixFileSystemPath(Model, TreeMixin):

    path = UnixAbsolutePathField(
        verbose_name=_("File Path"),
        help_text=_("Full or relative file path."),
        unique=True,
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

    size = BigIntegerField(
        verbose_name=_("Size (bytes)"),
        null=True,
        blank=True,
        help_text=_("Size of the file in bytes."),
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

    created = DateTimeField(
        verbose_name=_("Path creation date"),
    )

    modified = DateTimeField(
        verbose_name=_("Path modification date"),
    )

    last_accessed = DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Accessed date"),
    )

    description = TextField(
        blank=True,
        default='',
        verbose_name=_("Description"),
        help_text=_("Optional description or notes about this file."),
    )

    hash_md5 = MD5HashField(
        blank=True,
        null=True,
        verbose_name=_("MD5 Hash"),
        help_text=_("MD5 hash of the file content."),
    )

    hash_sha256 = SHA256HashField(
        blank=True,
        null=True,
        verbose_name=_("SHA256 Hash"),
        help_text=_("SHA256 hash of the file content."),
    )

    inode_id = BigIntegerField(
        blank=True,
        null=True,
        verbose_name=_("Inode ID"),
        help_text=_("Inode ID of the file."),
    )

    objects = UnixPathManager()

    class Meta:
        app_label = 'ahs_core'
        unique_together = (('path', 'inode_id'),)
        verbose_name = _("UNIX File")
        verbose_name_plural = _("UNIX Files")
        ordering = ['-modified', 'path']
        db_table = 'ahs_core_filesys_unixfile'

    def __str__(self):
        return f"{self.path} ({self.permissions})"

    def has_changed(self) -> bool:
        with open(self.path, 'rb') as f:
            new_sha256 = hashlib.sha256(f.read()).hexdigest()
            return self.hash_sha256 == new_sha256

    async def ahas_changed(self) -> bool:
        async with aopen_file(self.path, 'rb') as f:
            new_sha256 = hashlib.sha256(await f.read()).hexdigest()
            return self.hash_sha256 == new_sha256

    @property
    def mime_type(self) -> str:
        _magic = Magic(mime=True)
        return _magic.from_file(self.path)

    @property
    def file_extension(self) -> str:
        last_segment = self.path.rsplit("/", 1)[-1]
        return last_segment.split('.')[-1] if '.' in last_segment else ""

    def get_path_permissions(self):
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
            "path": self.path,
            "permissions": self.permissions,
            "permissions_display": self.get_path_permissions(),
            "uid": self.uid,
            "gid": self.gid,
            "size": self.size,
            "is_symlink": self.is_symlink,
            "symlink_target": self.symlink_target,
            "created": self.created,
            "modified": self.modified,
            "last_accessed": self.last_accessed,
            "description": self.description,
            "file_extension": self.file_extension,
            "mime_type": self.mime_type,
            "hash_md5": self.hash_md5,
            "hash_sha256": self.hash_sha256,
        }
        if include_directory:
            data['parent'] = str(self.parent) if self.parent else None

        return data
