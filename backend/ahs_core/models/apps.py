from django.db import models
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType


class AppManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)



class App(models.Model):
    """
    Represents an application entity within the system.

    This model is primarily designed to store metadata about an application,
    including its name, label, human-readable name, and cryptographic keys.
    Provides integration with Django's app framework through the `INSTALLED_APPS`
    setting. The generic relation attribute allows app-specific content to be
    linked dynamically via `ContentType`. Cryptographic functionality is also
    supported via the association with `:model:`ahs_crypto.PublicKey` and
    `:model:`ahs_crypto.PrivateKey`.

    Attributes:
        name (str): The application's name as defined in `INSTALLED_APPS`. Must
            be unique.
        label (str): Internal label used by Django for the application.
        verbose_name (str): Human-readable name of the application.
        public_key (:model:`ahs_crypto.PublicKey`): Foreign key linking the app
            to its public key used for cryptographic operations. Cannot be null.
        private_key (:model:`ahs_crypto.PrivateKey`): Foreign key linking the
            app to its private key used for cryptographic operations. Cannot be null.
            Blank values are allowed to facilitate initial data setup or
            troubleshooting.
        content_type (:model:`contenttypes.ContentType`): Optional generic
            relation enabling dynamic association with other models.

    Methods:
        set_private_key(private_key):
            Sets a new private key for the application. Saves the updated
            instance to the database.

            Parameters:
                private_key: A private key instance to assign.

        set_public_key(public_key):
            Associates a new public key with the application instance and
            persists this change to the database.

            Parameters:
                public_key: A public key instance to assign.

        __str__():
            Returns the human-readable name (`verbose_name`) of the application instance.

    Meta options:
        app_label: Specifies the app label as "ahs_core".
        verbose_name: Sets the singular human-readable name as "App".
        verbose_name_plural: Sets the plural human-readable name as "Apps".
        db_table: Specifies the database table name as "ahs_core_app".
        ordering: Orders query results by the `name` field in ascending order.
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

    # Generic relation
    content_type = models.ForeignKey(
        ContentType,
        on_delete=CASCADE,
        null=True,
        blank=True,
    )

    objects = AppManager()

    def __str__(self):
        return self.verbose_name

    class Meta:
        app_label = "ahs_core"
        db_table = "ahs_core_app"
        verbose_name = "App"
        verbose_name_plural = "Apps"
        ordering = ['name']
