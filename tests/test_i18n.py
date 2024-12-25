"""
Unit tests for internationalization functionality
Created by avixiii (https://avixiii.com)
"""
import pytest
from django.test import RequestFactory
from django.utils import translation
from seo_optimizer.i18n import (
    I18nMetadataManager,
    LocalizedURLManager,
    HrefLangGenerator,
    TimezoneManager
)


@pytest.mark.django_db
class TestI18nMetadataManager:
    def test_get_metadata(self, request_factory):
        # Setup
        request = request_factory.get('/')
        manager = I18nMetadataManager()
        
        # Execute
        with translation.override('fr'):
            metadata = manager.get_metadata('/test-page')
        
        # Assert
        assert metadata.language == 'fr'
        assert isinstance(metadata.title, str)
        assert isinstance(metadata.description, str)

    def test_metadata_cache(self, request_factory):
        # Setup
        manager = I18nMetadataManager()
        
        # Execute - First call
        metadata1 = manager.get_metadata('/test-page', 'en')
        
        # Execute - Second call (should hit cache)
        metadata2 = manager.get_metadata('/test-page', 'en')
        
        # Assert
        assert metadata1 == metadata2


class TestLocalizedURLManager:
    def test_get_language_url_prefix(self):
        # Setup
        url = '/test-page'
        
        # Execute
        result = LocalizedURLManager.get_language_url(url, 'fr')
        
        # Assert
        assert result == '/fr/test-page'

    def test_get_language_url_domain(self, settings):
        # Setup
        settings.SEO_I18N_URL_TYPE = 'domain'
        settings.SEO_I18N_DOMAIN_MAPPING = {'fr': 'fr.example.com'}
        url = '/test-page'
        
        # Execute
        result = LocalizedURLManager.get_language_url(url, 'fr')
        
        # Assert
        assert result == 'https://fr.example.com/test-page'


class TestHrefLangGenerator:
    def test_generate_tags(self, settings):
        # Setup
        settings.LANGUAGES = [
            ('en', 'English'),
            ('fr', 'French'),
            ('es', 'Spanish')
        ]
        generator = HrefLangGenerator('/test-page')
        
        # Execute
        tags = generator.generate_tags()
        
        # Assert
        assert len(tags) == 4  # 3 languages + x-default
        assert any(tag['hreflang'] == 'x-default' for tag in tags)
        assert any(tag['hreflang'] == 'en' for tag in tags)
        assert any(tag['hreflang'] == 'fr' for tag in tags)
        assert any(tag['hreflang'] == 'es' for tag in tags)


class TestTimezoneManager:
    def test_get_user_timezone_from_session(self, request_factory):
        # Setup
        request = request_factory.get('/')
        request.session = {'user_timezone': 'Europe/Paris'}
        
        # Execute
        timezone = TimezoneManager.get_user_timezone(request)
        
        # Assert
        assert timezone == 'Europe/Paris'

    def test_get_user_timezone_default(self, request_factory, settings):
        # Setup
        request = request_factory.get('/')
        request.session = {}
        settings.TIME_ZONE = 'UTC'
        
        # Execute
        timezone = TimezoneManager.get_user_timezone(request)
        
        # Assert
        assert timezone == 'UTC'
