from datetime import datetime

import pytz

from django import template

from django.template import Context
from django.utils.html import format_html
from django.utils.safestring import mark_safe


register = template.Library()


@register.inclusion_tag(filename='lib/_navbar.html', takes_context=True)
def navbar(context: Context, id, fixed):
    return {
        'id': id,
        'fixed': 'fixed-top' if fixed is True else '',
        'user': context['user'],
    }


@register.simple_tag(takes_context=True)
def current_datetime(context, format_string: str = '%Y-%m-%d %H:%M:%S') -> str:
    tz = context.get('timezone')
    if not tz:
        tz = 'UTC'
    return datetime.now(pytz.timezone(tz)).strftime(format_string)


@register.simple_tag(name='svg_icon')
def svg_icon(icon_name, extra_class=''):
    svg_tag = format_html(
        '<svg viewBox="0 0 512 512" width="10" height="10"'
        'class="icon-{name} {extra}">'
        '<use xlink:href="#{name}"></use>'
        '</svg>', name=icon_name, extra=extra_class)
    return mark_safe(svg_tag)
