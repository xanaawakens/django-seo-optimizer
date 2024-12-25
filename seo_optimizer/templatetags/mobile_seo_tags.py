"""
Template tags for mobile SEO support
Created by avixiii (https://avixiii.com)
"""
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from ..mobile import (
    MobileMetadataManager,
    ResponsiveDesignChecker,
    AMPGenerator,
    MobileFirstIndexing
)

register = template.Library()


@register.simple_tag(takes_context=True)
def render_mobile_meta(context):
    """
    Render mobile-specific meta tags
    Usage: {% render_mobile_meta %}
    """
    request = context.get('request')
    if not request:
        return ''

    manager = MobileMetadataManager()
    metadata = manager.get_metadata(request)

    return render_to_string('seo_optimizer/mobile_meta.html', {
        'metadata': metadata,
        'amp_url': context.get('amp_url')
    })


@register.simple_tag
def check_responsive_design(html_content):
    """
    Check if design is responsive
    Usage: {% check_responsive_design html_content as result %}
    """
    checker = ResponsiveDesignChecker(html_content)
    return checker.check_responsive_design()


@register.simple_tag
def generate_amp_version(html_content):
    """
    Generate AMP version of the content
    Usage: {% generate_amp_version html_content as amp_html %}
    """
    generator = AMPGenerator(html_content)
    return generator.generate_amp_html()


@register.simple_tag
def check_mobile_parity(url):
    """
    Check mobile-desktop content parity
    Usage: {% check_mobile_parity url as parity %}
    """
    indexing = MobileFirstIndexing()
    return indexing.check_mobile_parity(url)
