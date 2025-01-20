from django.contrib.auth import get_user_model
from django.db.models import Model, Manager, ForeignKey, CASCADE
from django.db.models.fields import CharField, BooleanField, DateTimeField

AHSUser = get_user_model()


class CommandLogManager(Manager):

    async def create_log(self, app_name, func_name, args, kwargs, web_socket=True):
        return await self.acreate(
            app_name=app_name,
            func_name=func_name,
            args=args,
            kwargs=kwargs,
            web_socket=web_socket,
        )


class CommandLog(Model):

    timestamp = DateTimeField(auto_now_add=True)
    page_name = ForeignKey(
        'core.Page',
        on_delete=CASCADE,
        related_name='command_logs',
        related_query_name='command_log',
    )
    app_name = CharField(max_length=255)
    func_name = CharField(max_length=255)
    args = CharField(max_length=255)
    kwargs = CharField(max_length=255)
    web_socket = BooleanField(default=True)
    user = ForeignKey(
        AHSUser,
        on_delete=CASCADE
    )

    objects = CommandLogManager()

    class Meta:
        app_label = 'core'
        verbose_name = 'Command Log'
        verbose_name_plural = 'Command Logs'
        ordering = ['-timestamp']
        get_latest_by = 'timestamp'
        unique_together = ('app_name', 'func_name', 'args', 'kwargs')
