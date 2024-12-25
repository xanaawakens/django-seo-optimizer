"""
SEO Analytics and Reporting functionality
Created by avixiii (https://avixiii.com)
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json
import asyncio
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.conf import settings


class AnalyticsConfig:
    """Configuration for SEO Analytics"""
    CACHE_TIMEOUT = getattr(settings, 'SEO_ANALYTICS_CACHE_TIMEOUT', 3600)
    MOBILE_USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
    DESKTOP_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'


@dataclass
class PageSpeed:
    """Container for page speed metrics"""
    load_time: float
    first_contentful_paint: float
    largest_contentful_paint: float
    time_to_interactive: float
    total_blocking_time: float


@dataclass
class ContentMetrics:
    """Container for content-related metrics"""
    word_count: int
    heading_structure: Dict[str, int]
    internal_links: int
    external_links: int
    broken_links: List[str]
    image_count: int
    images_with_alt: int
    keyword_density: Dict[str, float]


@dataclass
class TechnicalMetrics:
    """Container for technical SEO metrics"""
    has_ssl: bool
    has_robots_txt: bool
    has_sitemap: bool
    is_mobile_friendly: bool
    has_schema_markup: bool
    page_size: int
    response_time: float


@dataclass
class SEOReport:
    """Container for complete SEO analysis"""
    url: str
    timestamp: datetime
    title: str
    meta_description: str
    canonical_url: Optional[str]
    content_metrics: ContentMetrics
    technical_metrics: TechnicalMetrics
    page_speed: PageSpeed
    score: float
    suggestions: List[str]

    def to_dict(self) -> Dict:
        """Convert report to dictionary format"""
        return {
            'url': self.url,
            'timestamp': self.timestamp.isoformat(),
            'title': self.title,
            'meta_description': self.meta_description,
            'canonical_url': self.canonical_url,
            'content_metrics': {
                'word_count': self.content_metrics.word_count,
                'heading_structure': self.content_metrics.heading_structure,
                'internal_links': self.content_metrics.internal_links,
                'external_links': self.content_metrics.external_links,
                'broken_links': self.content_metrics.broken_links,
                'image_count': self.content_metrics.image_count,
                'images_with_alt': self.content_metrics.images_with_alt,
                'keyword_density': self.content_metrics.keyword_density
            },
            'technical_metrics': {
                'has_ssl': self.technical_metrics.has_ssl,
                'has_robots_txt': self.technical_metrics.has_robots_txt,
                'has_sitemap': self.technical_metrics.has_sitemap,
                'is_mobile_friendly': self.technical_metrics.is_mobile_friendly,
                'has_schema_markup': self.technical_metrics.has_schema_markup,
                'page_size': self.technical_metrics.page_size,
                'response_time': self.technical_metrics.response_time
            },
            'page_speed': {
                'load_time': self.page_speed.load_time,
                'first_contentful_paint': self.page_speed.first_contentful_paint,
                'largest_contentful_paint': self.page_speed.largest_contentful_paint,
                'time_to_interactive': self.page_speed.time_to_interactive,
                'total_blocking_time': self.page_speed.total_blocking_time
            },
            'score': self.score,
            'suggestions': self.suggestions
        }


class SEOAnalyzer:
    """Main class for SEO analysis"""

    def __init__(self):
        self.cache_timeout = AnalyticsConfig.CACHE_TIMEOUT

    async def analyze_url(self, url: str) -> SEOReport:
        """Analyze a URL and generate a complete SEO report"""
        cache_key = f"seo_report_{url}"
        cached_report = cache.get(cache_key)
        
        if cached_report:
            return SEOReport(**cached_report)

        # Fetch page content
        async with aiohttp.ClientSession() as session:
            start_time = datetime.now()
            async with session.get(url) as response:
                html_content = await response.text()
                response_time = (datetime.now() - start_time).total_seconds()

        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Gather metrics
        content_metrics = await self._analyze_content(soup, url)
        technical_metrics = await self._analyze_technical(url, response_time)
        page_speed = await self._analyze_page_speed(url)

        # Calculate score and generate suggestions
        score = self._calculate_score(content_metrics, technical_metrics, page_speed)
        suggestions = self._generate_suggestions(content_metrics, technical_metrics, page_speed)

        report = SEOReport(
            url=url,
            timestamp=datetime.now(),
            title=soup.title.string if soup.title else '',
            meta_description=self._get_meta_description(soup),
            canonical_url=self._get_canonical_url(soup),
            content_metrics=content_metrics,
            technical_metrics=technical_metrics,
            page_speed=page_speed,
            score=score,
            suggestions=suggestions
        )

        # Cache the report
        cache.set(cache_key, report.to_dict(), self.cache_timeout)
        return report

    async def _analyze_content(self, soup: BeautifulSoup, base_url: str) -> ContentMetrics:
        """Analyze content-related SEO metrics"""
        # Count words
        text_content = soup.get_text()
        word_count = len(text_content.split())

        # Analyze heading structure
        heading_structure = {}
        for i in range(1, 7):
            heading_structure[f'h{i}'] = len(soup.find_all(f'h{i}'))

        # Analyze links
        links = soup.find_all('a')
        internal_links = 0
        external_links = 0
        broken_links = []

        for link in links:
            href = link.get('href')
            if href:
                absolute_url = urljoin(base_url, href)
                if base_url in absolute_url:
                    internal_links += 1
                else:
                    external_links += 1
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.head(absolute_url) as response:
                            if response.status >= 400:
                                broken_links.append(absolute_url)
                except:
                    broken_links.append(absolute_url)

        # Analyze images
        images = soup.find_all('img')
        image_count = len(images)
        images_with_alt = len([img for img in images if img.get('alt')])

        # Calculate keyword density
        words = text_content.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        total_words = len(words)
        keyword_density = {
            word: count/total_words
            for word, count in word_freq.items()
            if count/total_words > 0.01  # Only include words that appear more than 1%
        }

        return ContentMetrics(
            word_count=word_count,
            heading_structure=heading_structure,
            internal_links=internal_links,
            external_links=external_links,
            broken_links=broken_links,
            image_count=image_count,
            images_with_alt=images_with_alt,
            keyword_density=keyword_density
        )

    async def _analyze_technical(self, url: str, response_time: float) -> TechnicalMetrics:
        """Analyze technical SEO metrics"""
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Check SSL
        has_ssl = parsed_url.scheme == 'https'

        # Check robots.txt
        robots_url = urljoin(base_url, '/robots.txt')
        has_robots_txt = False
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(robots_url) as response:
                    has_robots_txt = response.status == 200
            except:
                pass

        # Check sitemap
        sitemap_url = urljoin(base_url, '/sitemap.xml')
        has_sitemap = False
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(sitemap_url) as response:
                    has_sitemap = response.status == 200
            except:
                pass

        # Check mobile-friendliness
        is_mobile_friendly = await self._check_mobile_friendly(url)

        # Check schema markup
        has_schema_markup = bool(soup.find_all(
            ['script', 'meta'],
            attrs={'type': 'application/ld+json'}
        ))

        # Get page size
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                page_size = len(await response.read())

        return TechnicalMetrics(
            has_ssl=has_ssl,
            has_robots_txt=has_robots_txt,
            has_sitemap=has_sitemap,
            is_mobile_friendly=is_mobile_friendly,
            has_schema_markup=has_schema_markup,
            page_size=page_size,
            response_time=response_time
        )

    async def _analyze_page_speed(self, url: str) -> PageSpeed:
        """Analyze page speed metrics"""
        # This would typically use Google PageSpeed Insights API
        # For now, we'll use simple measurements
        async with aiohttp.ClientSession() as session:
            start_time = datetime.now()
            async with session.get(url) as response:
                await response.read()
                load_time = (datetime.now() - start_time).total_seconds()

        return PageSpeed(
            load_time=load_time,
            first_contentful_paint=load_time * 0.3,  # Simulated metrics
            largest_contentful_paint=load_time * 0.6,
            time_to_interactive=load_time * 0.8,
            total_blocking_time=load_time * 0.2
        )

    async def _check_mobile_friendly(self, url: str) -> bool:
        """Check if a page is mobile-friendly"""
        headers = {'User-Agent': AnalyticsConfig.MOBILE_USER_AGENT}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                # Check viewport meta tag
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                viewport = soup.find('meta', attrs={'name': 'viewport'})
                return bool(viewport)

    def _calculate_score(
        self,
        content_metrics: ContentMetrics,
        technical_metrics: TechnicalMetrics,
        page_speed: PageSpeed
    ) -> float:
        """Calculate overall SEO score"""
        score = 100.0
        
        # Content penalties
        if content_metrics.word_count < 300:
            score -= 10
        if not content_metrics.heading_structure.get('h1', 0):
            score -= 10
        if content_metrics.images_with_alt < content_metrics.image_count:
            score -= 5
        if content_metrics.broken_links:
            score -= len(content_metrics.broken_links) * 2

        # Technical penalties
        if not technical_metrics.has_ssl:
            score -= 20
        if not technical_metrics.has_robots_txt:
            score -= 5
        if not technical_metrics.has_sitemap:
            score -= 5
        if not technical_metrics.is_mobile_friendly:
            score -= 15
        if not technical_metrics.has_schema_markup:
            score -= 10
        if technical_metrics.response_time > 2:
            score -= 10

        # Page speed penalties
        if page_speed.load_time > 3:
            score -= 10
        if page_speed.largest_contentful_paint > 2.5:
            score -= 5
        if page_speed.time_to_interactive > 3.8:
            score -= 5

        return max(0, min(100, score))

    def _generate_suggestions(
        self,
        content_metrics: ContentMetrics,
        technical_metrics: TechnicalMetrics,
        page_speed: PageSpeed
    ) -> List[str]:
        """Generate SEO improvement suggestions"""
        suggestions = []

        # Content suggestions
        if content_metrics.word_count < 300:
            suggestions.append(_("Add more content - articles should be at least 300 words"))
        if not content_metrics.heading_structure.get('h1', 0):
            suggestions.append(_("Add an H1 heading to your page"))
        if content_metrics.images_with_alt < content_metrics.image_count:
            suggestions.append(_("Add alt text to all images"))
        if content_metrics.broken_links:
            suggestions.append(_("Fix broken links found on your page"))

        # Technical suggestions
        if not technical_metrics.has_ssl:
            suggestions.append(_("Enable HTTPS for your website"))
        if not technical_metrics.has_robots_txt:
            suggestions.append(_("Add a robots.txt file"))
        if not technical_metrics.has_sitemap:
            suggestions.append(_("Add an XML sitemap"))
        if not technical_metrics.is_mobile_friendly:
            suggestions.append(_("Optimize your page for mobile devices"))
        if not technical_metrics.has_schema_markup:
            suggestions.append(_("Add schema markup to your page"))
        if technical_metrics.response_time > 2:
            suggestions.append(_("Improve server response time"))

        # Page speed suggestions
        if page_speed.load_time > 3:
            suggestions.append(_("Optimize page load time"))
        if page_speed.largest_contentful_paint > 2.5:
            suggestions.append(_("Optimize Largest Contentful Paint"))
        if page_speed.time_to_interactive > 3.8:
            suggestions.append(_("Improve Time to Interactive"))

        return suggestions

    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description from HTML"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '') if meta_desc else ''

    def _get_canonical_url(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract canonical URL from HTML"""
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        return canonical.get('href') if canonical else None
