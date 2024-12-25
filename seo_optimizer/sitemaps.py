"""
Sitemap generation functionality for Django SEO Optimizer
Created by avixiii (https://avixiii.com)
"""
from typing import Dict, List, Any, Optional, Type
from datetime import datetime
from django.contrib.sitemaps import Sitemap
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _


class SitemapConfig:
    """Configuration for Sitemap generation"""
    CACHE_TIMEOUT = getattr(settings, 'SEO_SITEMAP_CACHE_TIMEOUT', 3600)
    DEFAULT_CHANGEFREQ = getattr(settings, 'SEO_SITEMAP_DEFAULT_CHANGEFREQ', 'weekly')
    DEFAULT_PRIORITY = getattr(settings, 'SEO_SITEMAP_DEFAULT_PRIORITY', 0.5)


class SitemapEntry(models.Model):
    """Model for storing custom sitemap entries"""
    url = models.CharField(_('URL'), max_length=255, unique=True)
    lastmod = models.DateTimeField(_('Last Modified'), default=timezone.now)
    changefreq = models.CharField(
        _('Change Frequency'),
        max_length=20,
        choices=[
            ('always', _('Always')),
            ('hourly', _('Hourly')),
            ('daily', _('Daily')),
            ('weekly', _('Weekly')),
            ('monthly', _('Monthly')),
            ('yearly', _('Yearly')),
            ('never', _('Never'))
        ],
        default=SitemapConfig.DEFAULT_CHANGEFREQ
    )
    priority = models.FloatField(
        _('Priority'),
        default=SitemapConfig.DEFAULT_PRIORITY,
        help_text=_('Priority from 0.0 to 1.0')
    )
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        verbose_name = _('Sitemap Entry')
        verbose_name_plural = _('Sitemap Entries')
        ordering = ['-priority', '-lastmod']

    def __str__(self):
        return self.url

    def clean(self):
        """Validate priority range"""
        if not 0.0 <= self.priority <= 1.0:
            raise ValueError(_('Priority must be between 0.0 and 1.0'))


class DynamicSitemap(Sitemap):
    """Dynamic sitemap that combines model-based and custom entries"""
    
    def __init__(self, model: Optional[Type[models.Model]] = None,
                 queryset=None, location_field: str = 'get_absolute_url'):
        self.model = model
        self.queryset = queryset
        self.location_field = location_field

    def items(self):
        """Get all items for the sitemap"""
        items = []
        
        # Add model-based items if specified
        if self.queryset is not None:
            items.extend(self.queryset)
        elif self.model is not None:
            items.extend(self.model.objects.all())
            
        # Add custom entries
        items.extend(SitemapEntry.objects.filter(is_active=True))
        
        return items

    def location(self, obj):
        """Get URL for the item"""
        if isinstance(obj, SitemapEntry):
            return obj.url
        if hasattr(obj, self.location_field):
            if callable(getattr(obj, self.location_field)):
                return getattr(obj, self.location_field)()
            return getattr(obj, self.location_field)
        return obj.get_absolute_url()

    def lastmod(self, obj):
        """Get last modification time"""
        if isinstance(obj, SitemapEntry):
            return obj.lastmod
        if hasattr(obj, 'updated_at'):
            return obj.updated_at
        if hasattr(obj, 'created_at'):
            return obj.created_at
        return None

    def changefreq(self, obj):
        """Get change frequency"""
        if isinstance(obj, SitemapEntry):
            return obj.changefreq
        return SitemapConfig.DEFAULT_CHANGEFREQ

    def priority(self, obj):
        """Get priority"""
        if isinstance(obj, SitemapEntry):
            return obj.priority
        return SitemapConfig.DEFAULT_PRIORITY


class SitemapManager:
    """Manager class for handling sitemaps"""
    
    def __init__(self):
        self.sitemaps: Dict[str, DynamicSitemap] = {}
        
    def register(self, name: str, model: Optional[Type[models.Model]] = None,
                queryset=None, location_field: str = 'get_absolute_url'):
        """Register a model or queryset for sitemap generation"""
        self.sitemaps[name] = DynamicSitemap(
            model=model,
            queryset=queryset,
            location_field=location_field
        )
        
    def get_sitemaps(self) -> Dict[str, DynamicSitemap]:
        """Get all registered sitemaps"""
        return self.sitemaps

    def add_entry(self, url: str, lastmod: Optional[datetime] = None,
                 changefreq: str = SitemapConfig.DEFAULT_CHANGEFREQ,
                 priority: float = SitemapConfig.DEFAULT_PRIORITY) -> SitemapEntry:
        """Add a custom sitemap entry"""
        entry = SitemapEntry(
            url=url,
            lastmod=lastmod or timezone.now(),
            changefreq=changefreq,
            priority=priority
        )
        entry.full_clean()
        entry.save()
        return entry
