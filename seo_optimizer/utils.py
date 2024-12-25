"""
Utility functions for SEO Optimizer
Created by avixiii (https://avixiii.com)
"""
from typing import Any, TypeVar, Type, Optional

T = TypeVar('T')

class NotSet:
    """Sentinel class for values that are not set"""
    pass

class Literal:
    """Class for literal values that should not be processed"""
    def __init__(self, value: Any):
        self.value = value

    def __str__(self) -> str:
        return str(self.value)

def get_current_site(request) -> Optional[Any]:
    """Get current site from request"""
    from django.contrib.sites.shortcuts import get_current_site
    try:
        return get_current_site(request)
    except Exception:
        return None

def get_site_by_domain(domain: str) -> Optional[Any]:
    """Get site by domain"""
    from django.contrib.sites.models import Site
    try:
        return Site.objects.get(domain=domain)
    except Site.DoesNotExist:
        return None
