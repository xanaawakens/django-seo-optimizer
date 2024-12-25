"""
Async utilities for Django SEO Optimizer
Created by avixiii (https://avixiii.com)
"""
from typing import Dict, Any, Optional, List
import asyncio
import aiohttp
from datetime import datetime
from django.core.cache import cache
from django.conf import settings
from .analytics import SEOAnalyzer
from .base import MetadataField


class AsyncConfig:
    """Configuration for async operations"""
    CACHE_TIMEOUT = getattr(settings, 'SEO_ASYNC_CACHE_TIMEOUT', 3600)
    MAX_CONCURRENT_REQUESTS = getattr(settings, 'SEO_MAX_CONCURRENT_REQUESTS', 10)
    REQUEST_TIMEOUT = getattr(settings, 'SEO_REQUEST_TIMEOUT', 30)


class AsyncMetadataManager:
    """Async manager for handling metadata operations"""
    
    def __init__(self):
        self.cache_timeout = AsyncConfig.CACHE_TIMEOUT
        self.semaphore = asyncio.Semaphore(AsyncConfig.MAX_CONCURRENT_REQUESTS)
        
    async def get_metadata(self, path: str) -> Dict[str, Any]:
        """
        Get metadata for a path asynchronously
        
        Args:
            path: URL path to get metadata for
            
        Returns:
            Dict containing metadata values
        """
        cache_key = f'async_metadata_{path}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        metadata = {}
        tasks = []
        
        # Create tasks for each registered field
        for field_name, field in MetadataField.get_registered_fields().items():
            if hasattr(field, 'get_value_async'):
                tasks.append(self._get_field_value(field, path))
            else:
                # Fall back to sync method if async not available
                metadata[field_name] = field.get_value(path)

        # Execute async tasks
        if tasks:
            results = await asyncio.gather(*tasks)
            for field_name, value in results:
                if value is not None:
                    metadata[field_name] = value

        cache.set(cache_key, metadata, timeout=self.cache_timeout)
        return metadata

    async def _get_field_value(self, field: MetadataField, path: str) -> tuple:
        """Get value for a single field asynchronously"""
        async with self.semaphore:
            value = await field.get_value_async(path)
            return field.name, value


class AsyncSEOAnalyzer:
    """Async version of SEO Analyzer"""
    
    def __init__(self):
        self.cache_timeout = AsyncConfig.CACHE_TIMEOUT
        self.semaphore = asyncio.Semaphore(AsyncConfig.MAX_CONCURRENT_REQUESTS)
        
    async def analyze_urls(self, urls: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple URLs concurrently
        
        Args:
            urls: List of URLs to analyze
            
        Returns:
            Dict containing analysis results for each URL
        """
        tasks = [self.analyze_url(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return dict(zip(urls, results))

    async def analyze_url(self, url: str) -> Dict[str, Any]:
        """
        Analyze a single URL asynchronously
        
        Args:
            url: URL to analyze
            
        Returns:
            Dict containing analysis results
        """
        cache_key = f'async_seo_analysis_{url}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data

        async with self.semaphore:
            async with aiohttp.ClientSession() as session:
                try:
                    start_time = datetime.now()
                    async with session.get(url, timeout=AsyncConfig.REQUEST_TIMEOUT) as response:
                        response_time = (datetime.now() - start_time).total_seconds()
                        content = await response.text()
                        
                        # Create analysis tasks
                        tasks = [
                            self._analyze_content(content, url),
                            self._analyze_technical(response, response_time),
                            self._analyze_page_speed(url)
                        ]
                        
                        content_metrics, technical_metrics, page_speed = await asyncio.gather(*tasks)
                        
                        # Calculate score and generate suggestions
                        score = self._calculate_score(content_metrics, technical_metrics, page_speed)
                        suggestions = self._generate_suggestions(content_metrics, technical_metrics, page_speed)
                        
                        result = {
                            'url': url,
                            'timestamp': datetime.now().isoformat(),
                            'content_metrics': content_metrics,
                            'technical_metrics': technical_metrics,
                            'page_speed': page_speed,
                            'score': score,
                            'suggestions': suggestions
                        }
                        
                        cache.set(cache_key, result, timeout=self.cache_timeout)
                        return result
                        
                except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                    return {
                        'url': url,
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    }

    async def _analyze_content(self, content: str, url: str) -> Dict[str, Any]:
        """Analyze content asynchronously"""
        # Implement content analysis logic here
        return {}

    async def _analyze_technical(self, response: aiohttp.ClientResponse, 
                               response_time: float) -> Dict[str, Any]:
        """Analyze technical aspects asynchronously"""
        # Implement technical analysis logic here
        return {}

    async def _analyze_page_speed(self, url: str) -> Dict[str, Any]:
        """Analyze page speed asynchronously"""
        # Implement page speed analysis logic here
        return {}

    def _calculate_score(self, content_metrics: Dict, technical_metrics: Dict,
                        page_speed: Dict) -> float:
        """Calculate overall SEO score"""
        # Implement scoring logic here
        return 0.0

    def _generate_suggestions(self, content_metrics: Dict, technical_metrics: Dict,
                            page_speed: Dict) -> List[str]:
        """Generate SEO improvement suggestions"""
        # Implement suggestion generation logic here
        return []
