"""
Field definitions for Django SEO Optimizer
Created by avixiii (https://avixiii.com)
"""
from typing import Any, Optional, Union, Type, List, Dict
from dataclasses import dataclass
import re
from urllib.parse import urlparse

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.conf import settings


@dataclass
class FieldOptions:
    """Options for metadata fields"""
    editable: bool = True
    populate_from: Optional[Union[str, callable]] = None
    default: Any = None
    verbose_name: Optional[str] = None
    help_text: Optional[str] = None
    validators: List[callable] = None


class MetadataField:
    """
    Base class for all metadata fields with enhanced validation
    """
    def __init__(
        self,
        max_length: int = 255,
        *,
        editable: bool = True,
        populate_from: Optional[Union[str, callable]] = None,
        default: Any = None,
        verbose_name: Optional[str] = None,
        help_text: Optional[str] = None,
        validators: List[callable] = None
    ):
        self.max_length = max_length
        self.options = FieldOptions(
            editable=editable,
            populate_from=populate_from,
            default=default,
            verbose_name=verbose_name,
            help_text=help_text,
            validators=validators or []
        )

    def get_field(self, **kwargs: Any) -> models.Field:
        """Get the Django model field for this metadata field"""
        return models.CharField(
            max_length=self.max_length,
            null=True,
            blank=True,
            **kwargs
        )

    def clean(self, value: Any) -> Any:
        """Clean and validate the field value"""
        if value is None:
            return self.options.default

        value = str(value)[:self.max_length]
        
        # Run custom validators
        for validator in self.options.validators:
            validator(value)
            
        return value


class TitleField(MetadataField):
    """
    Field for managing meta titles with length optimization
    """
    def __init__(
        self,
        max_length: int = 70,
        min_length: int = 30,
        **kwargs: Any
    ):
        super().__init__(max_length, **kwargs)
        self.min_length = min_length

    def clean(self, value: Any) -> str:
        """Clean and validate title"""
        value = super().clean(value)
        if value:
            if len(value) < self.min_length:
                raise ValidationError(
                    _("Title is too short. Minimum length is %(min)d characters."),
                    params={'min': self.min_length}
                )
        return value


class DescriptionField(MetadataField):
    """
    Field for managing meta descriptions with optimization hints
    """
    def __init__(
        self,
        max_length: int = 160,
        min_length: int = 50,
        **kwargs: Any
    ):
        super().__init__(max_length, **kwargs)
        self.min_length = min_length

    def clean(self, value: Any) -> str:
        """Clean and validate description"""
        value = super().clean(value)
        if value:
            if len(value) < self.min_length:
                raise ValidationError(
                    _("Description is too short. Minimum length is %(min)d characters."),
                    params={'min': self.min_length}
                )
        return value


class KeywordsField(MetadataField):
    """
    Field for managing meta keywords with validation and optimization
    """
    def __init__(
        self,
        max_length: int = 255,
        max_keywords: int = 10,
        min_keyword_length: int = 3,
        **kwargs: Any
    ):
        super().__init__(max_length, **kwargs)
        self.max_keywords = max_keywords
        self.min_keyword_length = min_keyword_length

    def clean(self, value: Any) -> str:
        """Clean and validate keywords"""
        if value is None:
            return ""
            
        if isinstance(value, (list, tuple)):
            keywords = [str(k).strip().lower() for k in value]
        else:
            keywords = [k.strip().lower() for k in str(value).split(',')]
            
        # Validate and filter keywords
        valid_keywords = []
        for keyword in keywords:
            if len(keyword) < self.min_keyword_length:
                continue
            if keyword not in valid_keywords:
                valid_keywords.append(keyword)
                
        # Limit number of keywords
        valid_keywords = valid_keywords[:self.max_keywords]
        
        return ','.join(valid_keywords)[:self.max_length]


class RobotsField(MetadataField):
    """
    Field for managing robots meta tag with validation
    """
    ROBOT_CHOICES = [
        ('index,follow', _('Index and Follow')),
        ('noindex,follow', _('No Index and Follow')),
        ('index,nofollow', _('Index and No Follow')),
        ('noindex,nofollow', _('No Index and No Follow')),
    ]

    def __init__(self, **kwargs: Any):
        kwargs.setdefault('max_length', 50)
        kwargs.setdefault('default', 'index,follow')
        super().__init__(**kwargs)

    def get_field(self, **kwargs: Any) -> models.Field:
        """Get the Django model field for robots"""
        return models.CharField(
            max_length=self.max_length,
            choices=self.ROBOT_CHOICES,
            default=self.options.default,
            **kwargs
        )

    def clean(self, value: Any) -> str:
        """Validate robots value"""
        if value is None:
            return self.options.default
            
        value = str(value).lower()
        valid_values = [choice[0] for choice in self.ROBOT_CHOICES]
        
        if value not in valid_values:
            raise ValidationError(
                _('Invalid robots value. Must be one of: %(valid)s'),
                params={'valid': ', '.join(valid_values)}
            )
            
        return value


class OpenGraphField(MetadataField):
    """
    Field for managing OpenGraph metadata with validation
    """
    def __init__(
        self,
        og_type: str = 'website',
        validate_image: bool = True,
        **kwargs: Any
    ):
        super().__init__(**kwargs)
        self.og_type = og_type
        self.validate_image = validate_image

    def clean(self, value: Any) -> Dict[str, str]:
        """Clean and validate OpenGraph data"""
        if isinstance(value, str):
            try:
                import json
                value = json.loads(value)
            except json.JSONDecodeError:
                value = {'url': value}

        if not isinstance(value, dict):
            raise ValidationError(_('OpenGraph value must be a dictionary or JSON string'))

        # Ensure required fields
        value['type'] = value.get('type', self.og_type)
        
        # Validate image URL if present and validation is enabled
        if self.validate_image and 'image' in value:
            image_url = value['image']
            parsed = urlparse(image_url)
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError(_('Invalid image URL'))

        return value


class CanonicalURLField(MetadataField):
    """
    Field for managing canonical URLs with validation
    """
    def __init__(self, **kwargs: Any):
        kwargs.setdefault('max_length', 2000)
        super().__init__(**kwargs)

    def clean(self, value: Any) -> str:
        """Clean and validate canonical URL"""
        if value is None:
            return None
            
        value = str(value)
        parsed = urlparse(value)
        
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError(_('Invalid canonical URL'))
            
        return value[:self.max_length]


class SchemaOrgField(MetadataField):
    """
    Field for managing Schema.org structured data
    """
    def __init__(
        self,
        schema_type: str = 'WebPage',
        **kwargs: Any
    ):
        kwargs.setdefault('max_length', 10000)
        super().__init__(**kwargs)
        self.schema_type = schema_type

    def clean(self, value: Any) -> Dict[str, Any]:
        """Clean and validate Schema.org data"""
        if isinstance(value, str):
            try:
                import json
                value = json.loads(value)
            except json.JSONDecodeError:
                raise ValidationError(_('Invalid JSON for Schema.org data'))

        if not isinstance(value, dict):
            raise ValidationError(_('Schema.org value must be a dictionary or JSON string'))

        # Ensure required fields
        value['@type'] = value.get('@type', self.schema_type)
        value['@context'] = 'https://schema.org'

        return value
