from django.db.models import CharField, ForeignKey, CASCADE, Model, BooleanField, DateTimeField
from django.db.models.fields import TextField, URLField, EmailField

from backend.core.models.host import Host
from backend.core.models.mixins import CreationDateMixin, UpdateDateMixin
from django.utils.translation import gettext_lazy as _

from backend.core.models.settings import AHSSettings


class Domain(Model, CreationDateMixin, UpdateDateMixin):
    """
    Represents a domain name entity in the system.

    The Domain class encapsulates data about domain names, including their
    top-level domains (TLDs), registration details, status, and associations
    with hosting entities. It also supports metadata for administrative
    and technical purposes.

    Inherits functionality for handling creation and update timestamps from
    :model:`core.CreationDateMixin` and :model:`core.UpdateDateMixin`.

    This model is used to associate domains with their respective hosting
    information and facilitate management of domain records.

    Attributes:
        domain_name (CharField):
            Fully qualified domain name (FQDN) of the entity, such as
            'example.com'.
        tld (CharField):
            Stores the top-level domain (TLD) as a string, such as 'com',
            'org', etc.
        host (ForeignKey):
            A foreign key pointing to the :model:`core.Host` model,
            representing the hosting entity for the domain. The relationship
            cascades on delete.
        is_active (BooleanField):
            Indicates whether the domain is currently active or inactive.
        registered_by (EmailField):
            Email address of the person or entity who registered the domain.
        admin_contact (CharField):
            Name of the administrative contact person for the domain.
        tech_contact (CharField):
            Name of the technical contact person for the domain.
        registrar_url (URLField):
            URL of the domain registrar managing the domain name.
        nameservers (TextField):
            List of nameservers associated with the domain, separated by
            commas. Example: "ns1.example.com, ns2.example.com".
        registration_date (DateTimeField):
            Timestamp indicating the domain’s registration date.
        expiry_date (DateTimeField):
            Timestamp indicating the domain’s expiration date.
        ssl_enabled (BooleanField):
            Specifies whether SSL is enabled for the domain.
        related_certificate (OneToOneField):
            A One-to-One relationship pointing to the SSL certificate
            object (if any) associated with the domain.
    """
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
        app_label = 'core'
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
    A centralized manager for accessing and handling different settings models.
    """

    @staticmethod
    def get_setting(key, fallback=None, model=None):
        """
        Retrieve a setting value by its key from the specified model.
        :param key: The name of the setting.
        :param fallback: The default value to return if no setting is found.
        :param model: The model to query (e.g., AHSSettings or DjangoSettings).
        :return: Setting value (or fallback if not found).
        """
        model = model or AHSSettings
        try:
            return model.objects.get(key=key).value
        except model.DoesNotExist:
            return fallback

    @staticmethod
    def set_setting(key, value, model=None):
        """
        Set or update a setting value by its key.
        :param key: The name of the setting.
        :param value: The value of the setting.
        :param model: The model to update (e.g., AHSSettings or DjangoSettings).
        """
        model = model or AHSSettings
        setting, created = model.objects.update_or_create(
            key=key,
            defaults={'value': value},
        )
        return setting

    @staticmethod
    def all_settings(model=None):
        """
        Fetch all settings stored within the specified model.
        :param model: The model to query (e.g., AHSSettings or DjangoSettings).
        :return: QuerySet of all settings.
        """
        model = model or AHSSettings
        return model.objects.all()
