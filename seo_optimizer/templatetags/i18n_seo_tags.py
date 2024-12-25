"""
Template tags for internationalization support
Created by avixiii (https://avixiii.com)
"""
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from ..i18n import (
    I18nMetadataManager,
    HrefLangGenerator,
    TimezoneManager
)

register = template.Library()


@register.simple_tag(takes_context=True)
def get_localized_metadata(context, language=None):
    """
    Get metadata for the current page in specified language
    Usage: {% get_localized_metadata 'en' as meta %}
    """
    request = context.get('request')
    if not request:
        return {}

    manager = I18nMetadataManager()
    return manager.get_metadata(request.path, language)


@register.simple_tag(takes_context=True)
def render_hreflang_tags(context):
    """
    Render hreflang tags for all supported languages
    Usage: {% render_hreflang_tags %}
    """
    request = context.get('request')
    if not request:
        return ''

    generator = HrefLangGenerator(request.path)
    tags = generator.generate_tags()

    return render_to_string('seo_optimizer/hreflang.html', {
        'hreflang_tags': tags
    })


@register.simple_tag(takes_context=True)
def get_user_timezone(context):
    """
    Get user's timezone
    Usage: {% get_user_timezone as user_tz %}
    """
    request = context.get('request')
    if not request:
        return ''

    return TimezoneManager.get_user_timezone(request)


@register.filter
def format_datetime(value, timezone=None):
    """
    Format datetime in user's timezone
    Usage: {{ my_datetime|format_datetime:user_tz }}
    """
    return TimezoneManager.format_datetime(value, timezone)
