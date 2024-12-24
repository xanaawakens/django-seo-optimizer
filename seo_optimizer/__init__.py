"""
Django SEO Optimizer - A powerful SEO optimization package
Created by avixiii (https://avixiii.com)
"""
from typing import Type, TypeVar, Optional

from django.apps import apps
from django.conf import settings

from .base import MetadataBase, register_metadata
from .fields import MetadataField, KeywordsField, RobotsField, OpenGraphField
from .models import setup
from .version import VERSION

__version__ = VERSION
__author__ = "avixiii"
__email__ = "contact@avixiii.com"
__website__ = "https://avixiii.com"

__all__ = [
    "register_metadata",
    "MetadataField",
    "KeywordsField",
    "RobotsField",
    "OpenGraphField",
    "setup",
]

# Setup the application
if apps.apps_ready and not hasattr(settings, "_SEO_OPTIMIZER_SETUP_DONE"):
    setup()
    settings._SEO_OPTIMIZER_SETUP_DONE = True
