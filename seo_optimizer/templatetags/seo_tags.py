"""
Template tags for Django SEO Optimizer
Created by avixiii (https://avixiii.com)
"""
from typing import Dict, Any, Optional
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.core.cache import cache
from ..base import MetadataField

register = template.Library()


@register.simple_tag(takes_context=True)
def get_metadata(context) -> Dict[str, Any]:
    """
    Get metadata for the current page
    Usage: {% get_metadata as meta %}
    """
    request = context.get('request')
    if not request:
        return {}

    # Try to get from cache first
    cache_key = f'seo_metadata_{request.path}'
    metadata = cache.get(cache_key)
    if metadata:
        return metadata

    # Get metadata from registered fields
    metadata = {}
    for field_name, field in MetadataField.get_registered_fields().items():
        value = field.get_value(request)
        if value:
            metadata[field_name] = value

    # Cache the result
    cache.set(cache_key, metadata, timeout=3600)
    return metadata


@register.simple_tag(takes_context=True)
def render_meta_tags(context) -> str:
    """
    Render all meta tags for the current page
    Usage: {% render_meta_tags %}
    """
    metadata = get_metadata(context)
    if not metadata:
        return ''

    meta_tags = []
    
    # Title tag
    if 'title' in metadata:
        meta_tags.append(f'<title>{metadata["title"]}</title>')

    # Meta description
    if 'description' in metadata:
        meta_tags.append(f'<meta name="description" content="{metadata["description"]}">')

    # Meta keywords
    if 'keywords' in metadata:
        keywords = metadata['keywords']
        if isinstance(keywords, (list, tuple)):
            keywords = ', '.join(keywords)
        meta_tags.append(f'<meta name="keywords" content="{keywords}">')

    # Robots
    if 'robots' in metadata:
        meta_tags.append(f'<meta name="robots" content="{metadata["robots"]}">')

    # Canonical URL
    if 'canonical_url' in metadata:
        meta_tags.append(f'<link rel="canonical" href="{metadata["canonical_url"]}">')

    # Open Graph tags
    og_tags = ['title', 'description', 'image', 'type', 'url']
    for tag in og_tags:
        og_key = f'og_{tag}'
        if og_key in metadata:
            meta_tags.append(f'<meta property="og:{tag}" content="{metadata[og_key]}">')

    # Twitter Card tags
    twitter_tags = ['card', 'site', 'creator', 'title', 'description', 'image']
    for tag in twitter_tags:
        twitter_key = f'twitter_{tag}'
        if twitter_key in metadata:
            meta_tags.append(f'<meta name="twitter:{tag}" content="{metadata[twitter_key]}">')

    return mark_safe('\n'.join(meta_tags))


@register.inclusion_tag('seo_optimizer/structured_data.html', takes_context=True)
def render_structured_data(context) -> Dict[str, Any]:
    """
    Render structured data (JSON-LD) for the current page
    Usage: {% render_structured_data %}
    """
    metadata = get_metadata(context)
    structured_data = metadata.get('structured_data', {})
    return {'structured_data': structured_data}


@register.simple_tag(takes_context=True)
def get_breadcrumbs(context) -> str:
    """
    Render SEO-friendly breadcrumbs
    Usage: {% get_breadcrumbs %}
    """
    request = context.get('request')
    if not request:
        return ''

    breadcrumbs = []
    path_parts = request.path.strip('/').split('/')
    current_path = ''

    for part in path_parts:
        if not part:
            continue
        current_path += f'/{part}'
        breadcrumbs.append({
            'title': part.replace('-', ' ').title(),
            'url': current_path
        })

    return render_to_string('seo_optimizer/breadcrumbs.html', {
        'breadcrumbs': breadcrumbs
    })
