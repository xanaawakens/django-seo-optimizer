"""
Internationalization support for Django SEO Optimizer
Created by avixiii (https://avixiii.com)
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from django.conf import settings
from django.utils import timezone, translation
from django.urls import reverse
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _


class I18nConfig:
    """Configuration for internationalization"""
    CACHE_TIMEOUT = getattr(settings, 'SEO_I18N_CACHE_TIMEOUT', 3600)
    DEFAULT_LANGUAGE = getattr(settings, 'LANGUAGE_CODE', 'en')
    SUPPORTED_LANGUAGES = getattr(settings, 'LANGUAGES', [('en', 'English')])
    URL_TYPE = getattr(settings, 'SEO_I18N_URL_TYPE', 'prefix')  # prefix or domain
    DOMAIN_MAPPING = getattr(settings, 'SEO_I18N_DOMAIN_MAPPING', {})


@dataclass
class LocalizedMetadata:
    """Container for localized metadata"""
    language: str
    title: str
    description: str
    keywords: List[str]
    canonical_url: str
    og_title: str
    og_description: str
    og_image: str
    twitter_title: str
    twitter_description: str
    twitter_image: str


class I18nMetadataManager:
    """Manager for handling localized metadata"""
    
    def __init__(self):
        self.cache_timeout = I18nConfig.CACHE_TIMEOUT
        
    def get_metadata(self, path: str, language: Optional[str] = None) -> LocalizedMetadata:
        """
        Get localized metadata for a path
        
        Args:
            path: URL path
            language: Language code (if None, uses current active language)
            
        Returns:
            LocalizedMetadata object
        """
        if language is None:
            language = translation.get_language() or I18nConfig.DEFAULT_LANGUAGE
            
        cache_key = f'i18n_metadata_{path}_{language}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
            
        # Get base metadata and localize it
        metadata = self._get_base_metadata(path)
        localized = self._localize_metadata(metadata, language)
        
        cache.set(cache_key, localized, timeout=self.cache_timeout)
        return localized
        
    def _get_base_metadata(self, path: str) -> Dict[str, Any]:
        """Get base metadata before localization"""
        # Implement base metadata retrieval logic
        return {}
        
    def _localize_metadata(self, metadata: Dict[str, Any], 
                          language: str) -> LocalizedMetadata:
        """Localize metadata for a specific language"""
        with translation.override(language):
            # Implement metadata localization logic
            return LocalizedMetadata(
                language=language,
                title=translation.gettext(metadata.get('title', '')),
                description=translation.gettext(metadata.get('description', '')),
                keywords=metadata.get('keywords', []),
                canonical_url=self._get_localized_url(
                    metadata.get('canonical_url', ''), 
                    language
                ),
                og_title=translation.gettext(metadata.get('og_title', '')),
                og_description=translation.gettext(metadata.get('og_description', '')),
                og_image=metadata.get('og_image', ''),
                twitter_title=translation.gettext(metadata.get('twitter_title', '')),
                twitter_description=translation.gettext(
                    metadata.get('twitter_description', '')
                ),
                twitter_image=metadata.get('twitter_image', '')
            )


class LocalizedURLManager:
    """Manager for handling localized URLs"""
    
    @staticmethod
    def get_language_url(url: str, language: str) -> str:
        """Get URL for a specific language"""
        if I18nConfig.URL_TYPE == 'domain':
            return LocalizedURLManager._get_domain_url(url, language)
        return LocalizedURLManager._get_prefix_url(url, language)
    
    @staticmethod
    def _get_domain_url(url: str, language: str) -> str:
        """Get domain-based language URL"""
        domain = I18nConfig.DOMAIN_MAPPING.get(language)
        if not domain:
            return url
        return f'https://{domain}{url}'
    
    @staticmethod
    def _get_prefix_url(url: str, language: str) -> str:
        """Get prefix-based language URL"""
        if language == I18nConfig.DEFAULT_LANGUAGE:
            return url
        return f'/{language}{url}'


class HrefLangGenerator:
    """Generator for hreflang tags"""
    
    def __init__(self, url: str):
        self.url = url
        self.url_manager = LocalizedURLManager()
        
    def generate_tags(self) -> List[Dict[str, str]]:
        """Generate hreflang tags for all supported languages"""
        tags = []
        
        for lang_code, lang_name in I18nConfig.SUPPORTED_LANGUAGES:
            tags.append({
                'hreflang': lang_code,
                'href': self.url_manager.get_language_url(self.url, lang_code)
            })
            
            # Add x-default tag for default language
            if lang_code == I18nConfig.DEFAULT_LANGUAGE:
                tags.append({
                    'hreflang': 'x-default',
                    'href': self.url_manager.get_language_url(
                        self.url, 
                        I18nConfig.DEFAULT_LANGUAGE
                    )
                })
                
        return tags


class TimezoneManager:
    """Manager for handling timezone-specific content"""
    
    @staticmethod
    def get_user_timezone(request) -> str:
        """Get user's timezone from request"""
        # Try to get from session
        tz = request.session.get('user_timezone')
        if tz:
            return tz
            
        # Try to get from Accept-Language header
        accept_lang = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
        if accept_lang:
            try:
                # Parse timezone from Accept-Language
                # This is a simplified example
                return 'UTC'
            except Exception:
                pass
                
        return settings.TIME_ZONE
        
    @staticmethod
    def format_datetime(dt, tz: Optional[str] = None):
        """Format datetime in user's timezone"""
        if tz:
            user_tz = timezone.pytz.timezone(tz)
            dt = timezone.localtime(dt, user_tz)
        return dt.isoformat()
