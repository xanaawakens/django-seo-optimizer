"""
Mobile SEO optimization functionality
Created by avixiii (https://avixiii.com)
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re
import json
from bs4 import BeautifulSoup
import requests
from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext_lazy as _


class MobileConfig:
    """Configuration for mobile SEO"""
    CACHE_TIMEOUT = getattr(settings, 'SEO_MOBILE_CACHE_TIMEOUT', 3600)
    VIEWPORT_WIDTH = getattr(settings, 'SEO_MOBILE_VIEWPORT_WIDTH', 375)
    ENABLE_AMP = getattr(settings, 'SEO_ENABLE_AMP', False)
    USER_AGENTS = {
        'mobile': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
        'desktop': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'googlebot': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'googlebot-mobile': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }


@dataclass
class ResponsiveCheck:
    """Container for responsive design check results"""
    viewport_meta: bool
    media_queries: bool
    image_sizing: bool
    tap_targets: bool
    font_size: bool
    no_horizontal_scroll: bool
    score: float
    issues: List[str]


@dataclass
class MobileMetadata:
    """Container for mobile-specific metadata"""
    viewport: str
    theme_color: str
    apple_mobile_web_app_capable: str
    format_detection: Dict[str, bool]
    smart_app_banner: Optional[str]
    manifest: Optional[str]


class MobileMetadataManager:
    """Manager for handling mobile-specific metadata"""
    
    def __init__(self):
        self.cache_timeout = MobileConfig.CACHE_TIMEOUT
        
    def get_metadata(self, request) -> MobileMetadata:
        """Get mobile-specific metadata"""
        cache_key = f'mobile_metadata_{request.path}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
            
        metadata = MobileMetadata(
            viewport=f'width={MobileConfig.VIEWPORT_WIDTH}, initial-scale=1',
            theme_color=self._get_theme_color(request),
            apple_mobile_web_app_capable='yes',
            format_detection={
                'telephone': True,
                'date': True,
                'address': True,
                'email': True
            },
            smart_app_banner=self._get_smart_app_banner(request),
            manifest=self._get_manifest_url(request)
        )
        
        cache.set(cache_key, metadata, timeout=self.cache_timeout)
        return metadata
        
    def _get_theme_color(self, request) -> str:
        """Get theme color for mobile browsers"""
        return getattr(settings, 'SEO_MOBILE_THEME_COLOR', '#000000')
        
    def _get_smart_app_banner(self, request) -> Optional[str]:
        """Get Smart App Banner content if configured"""
        return getattr(settings, 'SEO_SMART_APP_BANNER', None)
        
    def _get_manifest_url(self, request) -> Optional[str]:
        """Get Web App Manifest URL if configured"""
        return getattr(settings, 'SEO_WEB_APP_MANIFEST', None)


class ResponsiveDesignChecker:
    """Checker for responsive design implementation"""
    
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        
    def check_responsive_design(self) -> ResponsiveCheck:
        """Perform comprehensive responsive design check"""
        viewport_meta = self._check_viewport_meta()
        media_queries = self._check_media_queries()
        image_sizing = self._check_image_sizing()
        tap_targets = self._check_tap_targets()
        font_size = self._check_font_size()
        no_horizontal_scroll = self._check_horizontal_scroll()
        
        issues = []
        if not viewport_meta:
            issues.append(_('Missing viewport meta tag'))
        if not media_queries:
            issues.append(_('No media queries found'))
        if not image_sizing:
            issues.append(_('Images not properly sized for mobile'))
        if not tap_targets:
            issues.append(_('Tap targets too small or too close'))
        if not font_size:
            issues.append(_('Font size too small for mobile'))
        if not no_horizontal_scroll:
            issues.append(_('Page requires horizontal scrolling'))
            
        score = (sum([
            viewport_meta,
            media_queries,
            image_sizing,
            tap_targets,
            font_size,
            no_horizontal_scroll
        ]) / 6.0) * 100
        
        return ResponsiveCheck(
            viewport_meta=viewport_meta,
            media_queries=media_queries,
            image_sizing=image_sizing,
            tap_targets=tap_targets,
            font_size=font_size,
            no_horizontal_scroll=no_horizontal_scroll,
            score=score,
            issues=issues
        )
        
    def _check_viewport_meta(self) -> bool:
        """Check if viewport meta tag is properly set"""
        viewport = self.soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            return False
        content = viewport.get('content', '')
        return all(x in content for x in ['width', 'initial-scale'])
        
    def _check_media_queries(self) -> bool:
        """Check if CSS contains mobile media queries"""
        styles = self.soup.find_all('style')
        for style in styles:
            if '@media' in style.text:
                return True
        return False
        
    def _check_image_sizing(self) -> bool:
        """Check if images are properly sized"""
        images = self.soup.find_all('img')
        for img in images:
            if not img.get('srcset') and not img.get('sizes'):
                return False
        return True
        
    def _check_tap_targets(self) -> bool:
        """Check if tap targets are properly sized"""
        links = self.soup.find_all('a')
        buttons = self.soup.find_all('button')
        for element in links + buttons:
            style = element.get('style', '')
            if 'font-size' in style and int(re.search(r'font-size:\s*(\d+)px', style).group(1)) < 16:
                return False
        return True
        
    def _check_font_size(self) -> bool:
        """Check if font sizes are mobile-friendly"""
        elements = self.soup.find_all(['p', 'span', 'div'])
        for element in elements:
            style = element.get('style', '')
            if 'font-size' in style and int(re.search(r'font-size:\s*(\d+)px', style).group(1)) < 14:
                return False
        return True
        
    def _check_horizontal_scroll(self) -> bool:
        """Check if page requires horizontal scrolling"""
        elements = self.soup.find_all(style=re.compile(r'width:\s*\d+px'))
        for element in elements:
            width = int(re.search(r'width:\s*(\d+)px', element['style']).group(1))
            if width > MobileConfig.VIEWPORT_WIDTH:
                return False
        return True


class AMPGenerator:
    """Generator for AMP (Accelerated Mobile Pages) version"""
    
    def __init__(self, html_content: str):
        self.soup = BeautifulSoup(html_content, 'html.parser')
        
    def generate_amp_html(self) -> str:
        """Generate AMP version of the HTML content"""
        if not MobileConfig.ENABLE_AMP:
            return ''
            
        # Create AMP HTML structure
        amp_html = '<!doctype html>'
        amp_html += '<html ⚡>'
        amp_html += self._generate_amp_head()
        amp_html += self._generate_amp_body()
        amp_html += '</html>'
        
        return amp_html
        
    def _generate_amp_head(self) -> str:
        """Generate AMP-compatible head section"""
        head = '<head>'
        head += '<meta charset="utf-8">'
        head += '<script async src="https://cdn.ampproject.org/v0.js"></script>'
        
        # Convert canonical link
        canonical = self.soup.find('link', rel='canonical')
        if canonical:
            head += str(canonical)
            
        # Add AMP boilerplate
        head += '<style amp-boilerplate>body{-webkit-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-moz-animation:-amp-start 8s steps(1,end) 0s 1 normal both;-ms-animation:-amp-start 8s steps(1,end) 0s 1 normal both;animation:-amp-start 8s steps(1,end) 0s 1 normal both}@-webkit-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-moz-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-ms-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@-o-keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}@keyframes -amp-start{from{visibility:hidden}to{visibility:visible}}</style>'
        head += '<noscript><style amp-boilerplate>body{-webkit-animation:none;-moz-animation:none;-ms-animation:none;animation:none}</style></noscript>'
        
        # Convert styles to AMP custom styles
        styles = self.soup.find_all('style')
        if styles:
            amp_styles = '<style amp-custom>'
            for style in styles:
                amp_styles += style.string
            amp_styles += '</style>'
            head += amp_styles
            
        head += '</head>'
        return head
        
    def _generate_amp_body(self) -> str:
        """Generate AMP-compatible body section"""
        body = '<body>'
        
        # Convert images to amp-img
        images = self.soup.find_all('img')
        for img in images:
            amp_img = f'<amp-img src="{img.get("src", "")}" '
            amp_img += f'width="{img.get("width", "300")}" '
            amp_img += f'height="{img.get("height", "200")}" '
            amp_img += f'alt="{img.get("alt", "")}" layout="responsive"></amp-img>'
            body += amp_img
            
        # Convert iframes to amp-iframe
        iframes = self.soup.find_all('iframe')
        for iframe in iframes:
            amp_iframe = f'<amp-iframe src="{iframe.get("src", "")}" '
            amp_iframe += f'width="{iframe.get("width", "300")}" '
            amp_iframe += f'height="{iframe.get("height", "200")}" '
            amp_iframe += 'layout="responsive" sandbox="allow-scripts allow-same-origin">'
            amp_iframe += '<amp-img layout="fill" src="placeholder.png" placeholder></amp-img>'
            amp_iframe += '</amp-iframe>'
            body += amp_iframe
            
        body += '</body>'
        return body


class MobileFirstIndexing:
    """Handler for mobile-first indexing support"""
    
    def __init__(self):
        self.user_agents = MobileConfig.USER_AGENTS
        
    def check_mobile_parity(self, url: str) -> Dict[str, Any]:
        """Check content parity between mobile and desktop versions"""
        mobile_content = self._fetch_content(url, 'mobile')
        desktop_content = self._fetch_content(url, 'desktop')
        
        return {
            'content_match': self._compare_content(mobile_content, desktop_content),
            'mobile_friendly': self._check_mobile_friendly(mobile_content),
            'structured_data': self._compare_structured_data(mobile_content, desktop_content),
            'metadata': self._compare_metadata(mobile_content, desktop_content)
        }
        
    def _fetch_content(self, url: str, device: str) -> str:
        """Fetch content with specific user agent"""
        headers = {'User-Agent': self.user_agents[device]}
        response = requests.get(url, headers=headers)
        return response.text
        
    def _compare_content(self, mobile: str, desktop: str) -> bool:
        """Compare main content between mobile and desktop versions"""
        mobile_soup = BeautifulSoup(mobile, 'html.parser')
        desktop_soup = BeautifulSoup(desktop, 'html.parser')
        
        # Remove navigation, footer, etc.
        for soup in [mobile_soup, desktop_soup]:
            for tag in soup.find_all(['nav', 'footer', 'header']):
                tag.decompose()
                
        return mobile_soup.get_text() == desktop_soup.get_text()
        
    def _check_mobile_friendly(self, content: str) -> bool:
        """Check if content is mobile-friendly"""
        soup = BeautifulSoup(content, 'html.parser')
        checker = ResponsiveDesignChecker(str(soup))
        check_result = checker.check_responsive_design()
        return check_result.score >= 80
        
    def _compare_structured_data(self, mobile: str, desktop: str) -> bool:
        """Compare structured data between versions"""
        def extract_json_ld(html: str) -> List[Dict]:
            soup = BeautifulSoup(html, 'html.parser')
            scripts = soup.find_all('script', type='application/ld+json')
            data = []
            for script in scripts:
                try:
                    data.append(json.loads(script.string))
                except json.JSONDecodeError:
                    pass
            return data
            
        mobile_data = extract_json_ld(mobile)
        desktop_data = extract_json_ld(desktop)
        return mobile_data == desktop_data
        
    def _compare_metadata(self, mobile: str, desktop: str) -> bool:
        """Compare metadata between versions"""
        def extract_metadata(html: str) -> Dict[str, str]:
            soup = BeautifulSoup(html, 'html.parser')
            meta = {}
            for tag in soup.find_all('meta'):
                name = tag.get('name') or tag.get('property')
                if name:
                    meta[name] = tag.get('content', '')
            return meta
            
        mobile_meta = extract_metadata(mobile)
        desktop_meta = extract_metadata(desktop)
        return mobile_meta == desktop_meta
