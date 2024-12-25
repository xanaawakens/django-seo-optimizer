"""
Redirect Management functionality for Django SEO Optimizer
Created by avixiii (https://avixiii.com)
"""
from typing import Optional, List, Dict
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import re


class RedirectPattern(models.Model):
    """Model for managing URL redirects with pattern matching support"""
    url_pattern = models.CharField(
        _('URL Pattern'),
        max_length=255,
        help_text=_('URL pattern to match. Can include wildcards (*) and regex patterns if is_regex is True')
    )
    redirect_url = models.CharField(
        _('Redirect URL'),
        max_length=255,
        help_text=_('URL to redirect to. Can include capture group references ($1, $2, etc.) if using regex')
    )
    is_regex = models.BooleanField(
        _('Use Regex'),
        default=False,
        help_text=_('If True, the URL pattern will be treated as a regular expression')
    )
    status_code = models.IntegerField(
        _('HTTP Status Code'),
        choices=[
            (301, _('301 - Permanent Redirect')),
            (302, _('302 - Temporary Redirect')),
            (307, _('307 - Temporary Redirect (Preserves Method)')),
            (308, _('308 - Permanent Redirect (Preserves Method)'))
        ],
        default=301,
        help_text=_('HTTP status code to use for the redirect')
    )
    description = models.TextField(
        _('Description'),
        blank=True,
        help_text=_('Optional description of why this redirect exists')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    is_active = models.BooleanField(_('Active'), default=True)
    priority = models.IntegerField(
        _('Priority'),
        default=0,
        help_text=_('Higher priority redirects are checked first')
    )

    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = _('Redirect Pattern')
        verbose_name_plural = _('Redirect Patterns')
        indexes = [
            models.Index(fields=['url_pattern', 'is_active']),
            models.Index(fields=['priority'])
        ]

    def clean(self):
        """Validate the redirect pattern and URL"""
        if self.is_regex:
            try:
                re.compile(self.url_pattern)
            except re.error as e:
                raise ValidationError({
                    'url_pattern': _('Invalid regular expression: %(error)s') % {'error': str(e)}
                })
        
        # Validate redirect_url if it's not using capture groups
        if not any(f'${i}' in self.redirect_url for i in range(10)):
            validator = URLValidator()
            try:
                validator(self.redirect_url)
            except ValidationError:
                raise ValidationError({
                    'redirect_url': _('Enter a valid URL')
                })

    def __str__(self):
        return f'{self.url_pattern} -> {self.redirect_url} ({self.status_code})'


class RedirectManager:
    """Manager class for handling URL redirects"""
    
    def __init__(self):
        self.url_validator = URLValidator()
    
    def find_redirect(self, url: str) -> Optional[Dict]:
        """
        Find a matching redirect for the given URL
        
        Args:
            url: The URL to check for redirects
            
        Returns:
            Optional[Dict]: Dictionary containing redirect info if found, None otherwise
        """
        for redirect in RedirectPattern.objects.filter(is_active=True).order_by('-priority', '-created_at'):
            if redirect.is_regex:
                match = re.match(redirect.url_pattern, url)
                if match:
                    redirect_url = redirect.redirect_url
                    # Replace capture group references
                    for i, group in enumerate(match.groups(), start=1):
                        redirect_url = redirect_url.replace(f'${i}', group or '')
                    return {
                        'url': redirect_url,
                        'status_code': redirect.status_code
                    }
            else:
                # Handle wildcard patterns
                pattern = re.escape(redirect.url_pattern).replace('\\*', '.*')
                match = re.match(f'^{pattern}$', url)
                if match:
                    return {
                        'url': redirect.redirect_url,
                        'status_code': redirect.status_code
                    }
        return None

    def get_all_redirects(self) -> List[Dict]:
        """Get all active redirects"""
        return [{
            'pattern': redirect.url_pattern,
            'url': redirect.redirect_url,
            'status_code': redirect.status_code,
            'is_regex': redirect.is_regex,
            'priority': redirect.priority
        } for redirect in RedirectPattern.objects.filter(is_active=True).order_by('-priority', '-created_at')]

    def create_redirect(self, url_pattern: str, redirect_url: str, 
                       status_code: int = 301, is_regex: bool = False,
                       description: str = '', priority: int = 0) -> RedirectPattern:
        """Create a new redirect pattern"""
        redirect = RedirectPattern(
            url_pattern=url_pattern,
            redirect_url=redirect_url,
            status_code=status_code,
            is_regex=is_regex,
            description=description,
            priority=priority
        )
        redirect.full_clean()
        redirect.save()
        return redirect
