from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from backend.ahs_accounts.hashers import make_private_key
from backend.ahs_crypto import get_private_key_model, get_public_key_model

PrivateKey = get_private_key_model()
PublicKey = get_public_key_model()



class App(models.Model):
    """
    Model to represent applications installed in the Django project,
    with flexible relationships using GenericForeignKey.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Application Name",
        help_text=_("The name of the app as defined in INSTALLED_APPS."),
    )
    label = models.CharField(
        max_length=255,
        verbose_name="App Label",
        help_text=_("The label of the app, used internally by Django."),
    )
    verbose_name = models.CharField(
        max_length=255,
        verbose_name="Verbose Name",
        help_text=_("Human-readable name of the app."),
    )
    public_key = models.ForeignKey(
        PublicKey,
        on_delete=CASCADE,
        null=False,
        blank=True,
        verbose_name=_('Public Key'),
    )
    private_key = models.ForeignKey(
        PrivateKey,
        on_delete=CASCADE,
        null=False,
        blank=True,
        verbose_name=_('Private Key'),
    )

    # Generic relation
    content_type = models.ForeignKey(
        ContentType,
        on_delete=CASCADE,
        null=True,
        blank=True,
    )

    def set_private_key(self, private_key):
        self.private_key = make_private_key(private_key)
        self.save()

    def set_public_key(self, public_key):
        self.public_key = public_key
        self.save()

    def __str__(self):
        return self.verbose_name

    class Meta:
        app_label = "ahs_core"
        verbose_name = "App"
        verbose_name_plural = "Apps"
        db_table = "ahs_core_app"
        ordering = ['name']
