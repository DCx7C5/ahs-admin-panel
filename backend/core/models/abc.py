from uuid import uuid4

from django.db.models import UUIDField, CharField, Model, DateField

from backend.core.models.mixins import CreationDateMixin


class AbstractModel(Model):

    id = UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        auto_created=True,
    )

    class Meta:
        abstract = True


class AbstractEntity(AbstractModel):

    name = CharField(
        db_index=True,
        max_length=256,
        null=False,
        unique=False,
    )

    class Meta:
        abstract = True


class AbstractPerson(AbstractEntity):
    first_name = CharField(max_length=100,)
    birth_date = DateField()

    @property
    def full_name(self):
        return f"{self.first_name} {self.name}"

    class Meta:
        abstract = True


class AbstractEvent(AbstractModel, CreationDateMixin):

    message = CharField(max_length=256)

    class Meta:
        abstract = True


class AbstractMessage(AbstractEvent, ):
    class Meta:
        abstract = True

class AbstractPost(AbstractModel, CreationDateMixin):

    class Meta:
        abstract = True

class AbstractUserProfile(AbstractEntity, CreationDateMixin):
    user_name = CharField(max_length=100, null=False, unique=False)

    class Meta:
        abstract = True
