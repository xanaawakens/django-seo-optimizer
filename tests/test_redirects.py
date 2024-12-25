"""
Unit tests for redirects functionality
Created by avixiii (https://avixiii.com)
"""
import pytest
from django.test import RequestFactory
from seo_optimizer.redirects import RedirectManager, RedirectPattern


@pytest.mark.django_db
class TestRedirectManager:
    def test_find_redirect_exact_match(self, request_factory):
        # Setup
        request = request_factory.get('/old-page')
        pattern = RedirectPattern.objects.create(
            source_pattern='/old-page',
            target_url='/new-page',
            status_code=301,
            priority=100
        )
        
        # Execute
        manager = RedirectManager()
        redirect = manager.find_redirect(request)
        
        # Assert
        assert redirect is not None
        assert redirect.target_url == '/new-page'
        assert redirect.status_code == 301

    def test_find_redirect_regex_match(self, request_factory):
        # Setup
        request = request_factory.get('/product/123')
        pattern = RedirectPattern.objects.create(
            source_pattern=r'/product/(\d+)',
            target_url='/items/$1',
            status_code=302,
            priority=90,
            use_regex=True
        )
        
        # Execute
        manager = RedirectManager()
        redirect = manager.find_redirect(request)
        
        # Assert
        assert redirect is not None
        assert redirect.target_url == '/items/123'
        assert redirect.status_code == 302

    def test_find_redirect_wildcard_match(self, request_factory):
        # Setup
        request = request_factory.get('/blog/2023/12/post')
        pattern = RedirectPattern.objects.create(
            source_pattern='/blog/*/*/post',
            target_url='/articles/$1/$2/post',
            status_code=301,
            priority=80
        )
        
        # Execute
        manager = RedirectManager()
        redirect = manager.find_redirect(request)
        
        # Assert
        assert redirect is not None
        assert redirect.target_url == '/articles/2023/12/post'
        assert redirect.status_code == 301

    def test_find_redirect_no_match(self, request_factory):
        # Setup
        request = request_factory.get('/non-existent')
        
        # Execute
        manager = RedirectManager()
        redirect = manager.find_redirect(request)
        
        # Assert
        assert redirect is None

    def test_find_redirect_priority_order(self, request_factory):
        # Setup
        request = request_factory.get('/page')
        pattern1 = RedirectPattern.objects.create(
            source_pattern='/page',
            target_url='/page-v1',
            status_code=301,
            priority=100
        )
        pattern2 = RedirectPattern.objects.create(
            source_pattern='/page',
            target_url='/page-v2',
            status_code=301,
            priority=200
        )
        
        # Execute
        manager = RedirectManager()
        redirect = manager.find_redirect(request)
        
        # Assert
        assert redirect is not None
        assert redirect.target_url == '/page-v2'  # Higher priority wins
