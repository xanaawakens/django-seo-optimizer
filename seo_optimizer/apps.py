"""
Django application configuration for SEO Optimizer
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SEOOptimizerConfig(AppConfig):
    """Configuration for the SEO Optimizer application."""
    
    name = 'seo_optimizer'
    verbose_name = _("SEO Optimizer")
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        """
        Initialize the application when Django starts.
        This is called after the app registry is fully populated.
        """
        from django.conf import settings
        from .models import setup
        
        if not hasattr(settings, "_SEO_OPTIMIZER_SETUP_DONE"):
            setup()
            settings._SEO_OPTIMIZER_SETUP_DONE = True
            
        # Import signals
        from . import signals  # noqa
