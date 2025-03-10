from django.db.models import CharField, ForeignKey, CASCADE, Model, BooleanField, DateTimeField
from django.db.models.fields import TextField, URLField, EmailField

from backend.ahs_network.hosts.models import Host
from backend.ahs_settings.models import Settings
from backend.ahs_core.mixins import CreationDateMixin, UpdateDateMixin
from django.utils.translation import gettext_lazy as _



class Domain(Model, CreationDateMixin, UpdateDateMixin):
    domain_name = CharField(
        max_length=255,
        unique=True,
        help_text=_("The fully qualified domain name (FQDN), e.g., 'example.com'."),
        null=False,
        default="",
    )

    tld = CharField(
        max_length=63,
        verbose_name=_("Top-level domain (TLD)"),
        help_text=_("The top-level domain for this domain, e.g., 'com'."),
    )

    host = ForeignKey(
        to=Host,
        on_delete=CASCADE,
        verbose_name=_("Hosting Entity"),
        help_text=_("The host responsible for managing this domain."),
    )

    is_active = BooleanField(
        default=True,
        verbose_name=_("Active Status"),
        help_text=_("Specifies whether the domain is active."),
    )

    registered_by = EmailField(
        null=True,
        blank=True,
        verbose_name=_("Registrant Email"),
        help_text=_("Email address of the domain registrant."),
    )

    admin_contact = CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Admin Contact"),
        help_text=_("Name of the administrative contact for the domain."),
    )

    tech_contact = CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Technical Contact"),
        help_text=_("Name of the technical contact for the domain."),
    )

    registrar_url = URLField(
        null=True,
        blank=True,
        verbose_name=_("Registrar URL"),
        help_text=_("The URL of the domain registrar managing this domain."),
    )

    nameservers = TextField(
        null=True,
        blank=True,
        verbose_name=_("Nameservers"),
        help_text=_("Comma-separated list of nameservers, e.g., 'ns1.example.com, ns2.example.com'."),
    )

    registration_date = DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Registration Date"),
        help_text=_("The date and time when the domain was registered."),
    )

    expiry_date = DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Expiration Date"),
        help_text=_("The date and time when the domain will expire."),
    )

    ssl_enabled = BooleanField(
        default=False,
        verbose_name=_("SSL Enabled"),
        help_text=_("Specifies whether SSL is enabled for this domain."),
    )

    class Meta:
        app_label = 'ahs_core'
        verbose_name = 'Domain Name'
        verbose_name_plural = 'Domain Names'
        ordering = ['-registration_date']

    def is_expired(self):
        """
        Checks if the domain registration has expired.

        Returns:
            bool: True if the current date and time is greater than the expiry_date.
        """
        from django.utils.timezone import now
        return self.expiry_date and now() > self.expiry_date

    def __str__(self):
        """
        String representation of the domain.

        Returns:
            str: The domain name.
        """
        return self.domain_name


class UnifiedSettingsManager:
    """
    A centralized manager for accessing and handling different ahs_settings models.
    """

    @staticmethod
    def get_setting(key, fallback=None, model=None):
        model = model or Settings
        try:
            return model.objects.get(key=key).value
        except model.DoesNotExist:
            return fallback

    @staticmethod
    def set_setting(key, value, model=None):
        model = model or Settings
        setting, created = model.objects.update_or_create(
            key=key,
            defaults={'value': value},
        )
        return setting

    @staticmethod
    def all_settings(model=None):
        model = model or Settings
        return model.objects.all()
