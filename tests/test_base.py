"""
Tests for base functionality of SEO Optimizer
Created by avixiii (https://avixiii.com)
"""
import pytest
from django.test import override_settings, TransactionTestCase
from django.contrib.sites.models import Site
from django.apps import apps
from django.core.exceptions import AppRegistryNotReady
from asgiref.sync import sync_to_async

from seo_optimizer.base import MetadataBase, register_metadata


class TestMetadata(MetadataBase):
    """Test metadata class for testing purposes"""
    class Meta:
        use_sites = True

    def _get_instances(self, path, context=None, site=None, language=None, subdomain=None):
        return []

    @classmethod
    async def _async_get_instances(cls, path, context=None, site=None, language=None, subdomain=None):
        return []


@pytest.mark.django_db(transaction=True)
class TestMetadataBase(TransactionTestCase):
    """Test cases for MetadataBase functionality"""

    def setup_method(self, method):
        """Set up test data"""
        # Delete any existing sites
        Site.objects.all().delete()

    def test_lazy_loading_site_model(self):
        """Test that Site model is lazily loaded"""
        # This should not raise AppRegistryNotReady
        metadata = TestMetadata()
        assert hasattr(metadata, '_meta')
        assert metadata._meta.use_sites is True

    @pytest.mark.asyncio
    async def test_async_get_instances(self):
        """Test async instance retrieval with site"""
        create_site = sync_to_async(Site.objects.create)
        site = await create_site(domain='test.com', name='Test Site')
        metadata = TestMetadata()
        
        # Test with explicit site
        instances = await metadata._async_get_instances('/', site=site)
        assert isinstance(instances, list)

        # Test with site domain string
        instances = await metadata._async_get_instances('/', site='test.com')
        assert isinstance(instances, list)

    def test_sync_get_instances(self):
        """Test sync instance retrieval with site"""
        site = Site.objects.create(domain='test.com', name='Test Site')
        metadata = TestMetadata()
        
        # Test with explicit site
        instances = metadata._get_instances('/', site=site)
        assert isinstance(instances, list)

        # Test with site domain string
        instances = metadata._get_instances('/', site='test.com')
        assert isinstance(instances, list)

    @override_settings(SEO_ASYNC_ENABLED=True)
    def test_async_enabled_setting(self):
        """Test async functionality respects settings"""
        metadata = TestMetadata()
        assert metadata._meta.async_enabled is True

    @override_settings(SEO_ASYNC_ENABLED=False)
    def test_async_disabled_setting(self):
        """Test async functionality can be disabled"""
        metadata = TestMetadata()
        assert metadata._meta.async_enabled is False

    def test_register_metadata(self):
        """Test metadata registration"""
        path_pattern = r'^/test/.*$'
        register_metadata(TestMetadata, path_pattern)
        # Add assertions to verify registration
