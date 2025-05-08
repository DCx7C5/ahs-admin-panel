from django.db.models import (
    Model,
    CASCADE,
    OneToOneField,
    CharField,
    TextChoices,
    ForeignKey,
    DateTimeField,
    IntegerField,
)
from django.urls import reverse
from django.utils.translation import gettext as _

from backend.ahs_network.domains.models import Domain
from backend.ahs_network.hosts.models import Host
from backend.ahs_network.ipaddresses.models import IPAddress


class HTTPMethod(TextChoices):
    GET = 'GET', 'GET'
    POST = 'POST', 'POST'
    PUT = 'PUT', 'PUT'
    DELETE = 'DELETE', 'DELETE'
    PATCH = 'PATCH', 'PATCH'
    HEAD = 'HEAD', 'HEAD'
    OPTIONS = 'OPTIONS', 'OPTIONS'
    TRACE = 'TRACE', 'TRACE'
    CONNECT = 'CONNECT', 'CONNECT'


class HTTPProtocols(TextChoices):
    HTTP = 'HTTP', 'HTTP'
    HTTPS = 'HTTPS', 'HTTPS'


class UserAgent(Model):
    type = CharField(
        max_length=32,
        help_text=_('Name of the user agent.'),
    )
    value = CharField(
        max_length=1024,
        help_text=_('Value of the user agent type.'),
    )

    class Meta:
        app_label = 'ahs_network'
        verbose_name = 'User Agent'
        verbose_name_plural = 'User Agents'
        ordering = ['type', 'value']
        db_table = 'ahs_network_http_useragents'


class HTTPRequest(Model):

    # noinspection PyTypeChecker
    method = CharField(
        choices=HTTPMethod,
        max_length=7,
        default=HTTPMethod.GET,
    )

    # noinspection PyTypeChecker
    protocol = CharField(
        choices=HTTPProtocols,
        max_length=5,
        default=HTTPProtocols.HTTPS,
    )

    domain = ForeignKey(
        Domain,
        on_delete=CASCADE,
        related_name='http_requests',
        null=True,
        blank=True,
        help_text=_('Domain (if applicable) for this request.'),
    )

    port = IntegerField(
        null=True,
        blank=True,
        verbose_name='Port Number',
        help_text=_('Port number used (if applicable).'),
    )

    path = CharField(
        max_length=2048,
        blank=True,
        help_text=_("Requested path or URL fragment (not including domain)."),
    )

    query_string = CharField(
        max_length=4096,
        blank=True,
        help_text=_("Query string, if present."),
    )

    host = ForeignKey(
        Host,
        on_delete=CASCADE,
        related_name='http_requests',
        null=True,
        blank=True,
        help_text=_("Host object for this request."),
    )

    ip_address = ForeignKey(
        IPAddress,
        on_delete=CASCADE,
        related_name='http_requests',
        null=True,
        blank=True,
        help_text=_("IP address the request was sent to."),
    )

    created_at = DateTimeField(
        auto_now_add=True,
        help_text=_("When this request was recorded."),
    )

    class Meta:
        app_label = 'ahs_network'
        verbose_name = 'HTTP Request'
        verbose_name_plural = 'HTTP Requests'
        ordering = ['-created_at']
        db_table = 'ahs_network_http_requests'

    def __str__(self):
        return f"{self.method} {self.path}"

    def get_absolute_url(self):
        return reverse('http:http_request_detail', kwargs={'pk': self.pk})


class HTTPResponse(Model):


    request = OneToOneField(
        HTTPRequest,
        on_delete=CASCADE,
        related_query_name='response',
        verbose_name='Http Request',
        help_text=_('The HTTP request that this response belongs to.')
    )


    class Meta:
        app_label = 'ahs_network'
        verbose_name = 'HTTP Response'
        verbose_name_plural = 'HTTP Responses'
        ordering = ['-request__created_at']
        db_table = 'ahs_network_http_responses'

