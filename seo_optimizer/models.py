"""
Models for SEO Optimizer
Created by avixiii (https://avixiii.com)
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.apps import apps

def setup():
    """Setup function called during Django initialization"""
    pass  # We'll implement this later if needed

class SEOMetadata(models.Model):
    """Base model for SEO metadata"""
    path = models.CharField(_('Path'), max_length=255)
    site = models.ForeignKey('sites.Site', on_delete=models.CASCADE, related_name='seo_metadata')
    title = models.CharField(_('Title'), max_length=255, blank=True)
    description = models.TextField(_('Description'), blank=True)
    keywords = models.CharField(_('Keywords'), max_length=255, blank=True)
    robots = models.CharField(_('Robots'), max_length=255, blank=True)
    canonical_url = models.URLField(_('Canonical URL'), blank=True)
    og_title = models.CharField(_('Open Graph Title'), max_length=255, blank=True)
    og_description = models.TextField(_('Open Graph Description'), blank=True)
    og_image = models.URLField(_('Open Graph Image'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('SEO Metadata')
        verbose_name_plural = _('SEO Metadata')
        unique_together = ('path', 'site')
        ordering = ('-updated_at',)

    def __str__(self):
        return f"{self.site.domain}{self.path}"
