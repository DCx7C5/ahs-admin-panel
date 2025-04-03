
from asgiref.sync import sync_to_async
from django.contrib.sessions.backends.base import UpdateError, CreateError
from django.db import DatabaseError, IntegrityError, transaction, router
from django.utils import timezone

from django.utils.functional import cached_property

from django.contrib.sessions.backends.db import SessionStore as DBSessionStore


class SessionStore(DBSessionStore):
    """
    Implement database session store.
    """

    def __init__(self, session_key=None):
        super().__init__(session_key)

    @classmethod
    def get_model_class(cls):
        # Avoids a circular import and allows importing SessionStore when
        # django.contrib.sessions is not in INSTALLED_APPS.
        from backend.ahs_core.models import AHSSession
        return AHSSession

    @cached_property
    def model(self):
        return self.get_model_class()

    def create_model_instance(self):
        """
        Return a new instance of the session model object, which represents the
        current session state. Intended to be used for saving the session data
        to the database.
        """
        return self.model(
            session_key=self._get_or_create_session_key(),
            expire_date=self.get_expiry_date(),
        )

    async def acreate_model_instance(self):
        """See create_model_instance()."""
        return self.model(
            session_key=await self._aget_or_create_session_key(),
            expire_date=await self.aget_expiry_date(),
        )

    def save(self, must_create=False):
        """
        Save the current session data to the database. If 'must_create' is
        True, raise a database error if the saving operation doesn't create a
        new entry (as opposed to possibly updating an existing entry).
        """
        if self.session_key is None:
            return self.create()
        obj = self.create_model_instance()
        using = router.db_for_write(self.model, instance=obj)
        try:
            with transaction.atomic(using=using):
                obj.save(
                    force_insert=must_create, force_update=not must_create, using=using
                )
        except IntegrityError:
            if must_create:
                raise CreateError
            raise
        except DatabaseError:
            if not must_create:
                raise UpdateError
            raise

    async def asave(self, must_create=False):
        """See save()."""
        if self.session_key is None:
            return await self.acreate()
        obj = await self.acreate_model_instance()
        using = router.db_for_write(self.model, instance=obj)
        try:
            # This code MOST run in a transaction, so it requires
            # @sync_to_async wrapping until transaction.atomic() supports
            # async.
            @sync_to_async
            def sync_transaction():
                with transaction.atomic(using=using):
                    obj.save(
                        force_insert=must_create,
                        force_update=not must_create,
                        using=using,
                    )

            await sync_transaction()
        except IntegrityError:
            if must_create:
                raise CreateError
            raise
        except DatabaseError:
            if not must_create:
                raise UpdateError
            raise

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        try:
            self.model.objects.get(session_key=session_key).delete()
        except self.model.DoesNotExist:
            pass

    async def adelete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        try:
            obj = await self.model.objects.aget(session_key=session_key)
            await obj.adelete()
        except self.model.DoesNotExist:
            pass

    @classmethod
    def clear_expired(cls):
        cls.get_model_class().objects.filter(expire_date__lt=timezone.now()).delete()

    @classmethod
    async def aclear_expired(cls):
        await cls.get_model_class().objects.filter(
            expire_date__lt=timezone.now()
        ).adelete()


