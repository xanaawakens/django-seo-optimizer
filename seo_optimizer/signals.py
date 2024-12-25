"""
Signal handlers for SEO Optimizer
Created by avixiii (https://avixiii.com)
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.sites.models import Site

from .models import SEOMetadata

@receiver(post_save, sender=Site)
def handle_site_save(sender, instance, created, **kwargs):
    """Handle Site model save signal"""
    # Add any site-related cleanup or cache invalidation here
    pass

@receiver(post_delete, sender=Site)
def handle_site_delete(sender, instance, **kwargs):
    """Handle Site model delete signal"""
    # Add any site-related cleanup here
    pass

@receiver(post_save, sender=SEOMetadata)
def handle_metadata_save(sender, instance, created, **kwargs):
    """Handle SEOMetadata model save signal"""
    # Add any metadata-related cache invalidation here
    pass

@receiver(post_delete, sender=SEOMetadata)
def handle_metadata_delete(sender, instance, **kwargs):
    """Handle SEOMetadata model delete signal"""
    # Add any metadata-related cleanup here
    pass
