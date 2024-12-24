"""
Django application configuration for SEO Optimizer
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SeoOptimizerConfig(AppConfig):
    """Configuration for the SEO Optimizer application."""
    
    name = 'seo_optimizer'
    verbose_name = _("SEO Optimizer")
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """
        Initialize the application when Django starts.
        """
        from . import signals  # noqa
