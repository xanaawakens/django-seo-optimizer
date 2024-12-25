"""
Unit tests for mobile SEO functionality
Created by avixiii (https://avixiii.com)
"""
import pytest
from django.test import RequestFactory
from seo_optimizer.mobile import (
    MobileMetadataManager,
    ResponsiveDesignChecker,
    AMPGenerator,
    MobileFirstIndexing
)


class TestMobileMetadataManager:
    def test_get_metadata(self, request_factory):
        # Setup
        request = request_factory.get('/')
        manager = MobileMetadataManager()
        
        # Execute
        metadata = manager.get_metadata(request)
        
        # Assert
        assert metadata.viewport == 'width=375, initial-scale=1'
        assert metadata.apple_mobile_web_app_capable == 'yes'
        assert metadata.format_detection['telephone'] is True


class TestResponsiveDesignChecker:
    def test_check_responsive_design(self, mock_html_content):
        # Setup
        checker = ResponsiveDesignChecker(mock_html_content)
        
        # Execute
        result = checker.check_responsive_design()
        
        # Assert
        assert result.viewport_meta is True
        assert result.media_queries is True
        assert result.image_sizing is True
        assert result.tap_targets is True
        assert result.score >= 80

    def test_check_viewport_meta(self, mock_html_content):
        # Setup
        checker = ResponsiveDesignChecker(mock_html_content)
        
        # Execute
        result = checker._check_viewport_meta()
        
        # Assert
        assert result is True

    def test_check_media_queries(self, mock_html_content):
        # Setup
        checker = ResponsiveDesignChecker(mock_html_content)
        
        # Execute
        result = checker._check_media_queries()
        
        # Assert
        assert result is True


class TestAMPGenerator:
    def test_generate_amp_html(self, mock_html_content):
        # Setup
        generator = AMPGenerator(mock_html_content)
        
        # Execute
        amp_html = generator.generate_amp_html()
        
        # Assert
        assert '⚡' in amp_html
        assert 'amp-img' in amp_html
        assert 'amp-boilerplate' in amp_html

    def test_generate_amp_head(self, mock_html_content):
        # Setup
        generator = AMPGenerator(mock_html_content)
        
        # Execute
        head = generator._generate_amp_head()
        
        # Assert
        assert 'cdn.ampproject.org' in head
        assert 'amp-boilerplate' in head


@pytest.mark.django_db
class TestMobileFirstIndexing:
    def test_check_mobile_parity(self, mocker):
        # Setup
        indexing = MobileFirstIndexing()
        mock_mobile = mock_html_content
        mock_desktop = mock_html_content
        mocker.patch.object(
            indexing, 
            '_fetch_content',
            side_effect=[mock_mobile, mock_desktop]
        )
        
        # Execute
        result = indexing.check_mobile_parity('http://example.com')
        
        # Assert
        assert result['content_match'] is True
        assert result['mobile_friendly'] is True
        assert result['structured_data'] is True
        assert result['metadata'] is True
