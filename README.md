# Django SEO Optimizer

[![PyPI version](https://badge.fury.io/py/django-seo-optimizer.svg)](https://badge.fury.io/py/django-seo-optimizer)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-seo-optimizer.svg)](https://pypi.org/project/django-seo-optimizer/)
[![Django Versions](https://img.shields.io/pypi/djversions/django-seo-optimizer.svg)](https://pypi.org/project/django-seo-optimizer/)
[![License](https://img.shields.io/github/license/avixiii-dev/django-seo-optimizer.svg)](https://github.com/avixiii-dev/django-seo-optimizer/blob/main/LICENSE)

A powerful Django SEO optimization package that helps you manage and optimize your website's SEO with modern Python features and best practices.

## Features

- 🚀 Modern Python (3.8+) & Django (3.2+) compatibility
- 🎯 Smart metadata management with multiple backend support
- 🌐 Advanced site-specific SEO optimization
- 🔄 Intelligent redirect management with pattern matching
- 🎨 Dynamic template support in metadata
- ⚡ Performance-optimized with async support and caching
- 🔍 Advanced URL pattern matching and routing
- 🌍 Comprehensive i18n/l10n support
- 🔒 Type hints and modern Python features
- 📊 SEO performance analytics and reporting
- 🤖 Automated meta tag optimization
- 🔗 Sitemap generation and management
- 📱 Mobile SEO optimization support

## Installation

```bash
pip install django-seo-optimizer
```

## Quick Start

1. Add 'seo_optimizer' to your INSTALLED_APPS:

```python
INSTALLED_APPS = [
    ...
    'seo_optimizer',
]
```

2. Run migrations:

```bash
python manage.py migrate seo_optimizer
```

3. Configure your SEO metadata:

```python
from seo_optimizer import register_metadata, MetadataField

@register_metadata
class MyMetadata:
    title = MetadataField(max_length=70)
    description = MetadataField(max_length=160)
    keywords = KeywordsField()
    robots = RobotsField()
```

4. Use in your templates:

```html
{% load seo_tags %}
{% get_metadata as meta %}

<title>{{ meta.title }}</title>
<meta name="description" content="{{ meta.description }}">
<meta name="keywords" content="{{ meta.keywords }}">
<meta name="robots" content="{{ meta.robots }}">
```

## Advanced Features

### Async Support

```python
from seo_optimizer.async_utils import AsyncMetadataManager

async def get_optimized_metadata(path):
    manager = AsyncMetadataManager()
    metadata = await manager.get_metadata(path)
    return metadata
```

### Pattern-based Redirects

```python
from seo_optimizer.models import RedirectPattern

RedirectPattern.objects.create(
    url_pattern="/old-blog/*",
    redirect_url="/blog/$1",
    is_regex=True,
    status_code=301
)
```

### Performance Analytics

```python
from seo_optimizer.analytics import SEOAnalytics

analytics = SEOAnalytics()
report = analytics.generate_report()
print(report.suggestions)
```

## API Documentation

### Core Components

#### MetadataField

The base field type for SEO metadata:

```python
from seo_optimizer import MetadataField

title = MetadataField(
    max_length=70,
    required=True,
    template_support=True
)
```

**Parameters:**
- `max_length`: Maximum length of the field value
- `required`: Whether the field is required
- `template_support`: Enable Django template syntax in field values
- `validators`: List of validation functions

#### Specialized Fields

```python
from seo_optimizer import KeywordsField, RobotsField, OpenGraphField

# Keywords with automatic comma separation
keywords = KeywordsField(max_keywords=10)

# Robots directives with validation
robots = RobotsField(default="index,follow")

# Open Graph metadata
og = OpenGraphField(
    title_max_length=95,
    description_max_length=200
)
```

#### AsyncMetadataManager

For high-performance async metadata operations:

```python
from seo_optimizer import AsyncMetadataManager

async def get_meta(path):
    manager = AsyncMetadataManager()
    return await manager.get_metadata(path)
```

### Configuration Options

Available settings in `settings.py`:

```python
SEO_OPTIMIZER = {
    'CACHE_TIMEOUT': 3600,  # 1 hour
    'ASYNC_ENABLED': True,
    'MAX_ASYNC_WORKERS': 10,
    'USE_SITES_FRAMEWORK': True,
    'DEFAULT_LANGUAGE': 'en',
}
```

## User Guide

### Basic Setup

1. Install the package:
```bash
pip install django-seo-optimizer
```

2. Add to INSTALLED_APPS:
```python
INSTALLED_APPS = [
    ...
    'seo_optimizer',
]
```

3. Run migrations:
```bash
python manage.py migrate seo_optimizer
```

### Metadata Configuration

Create a metadata configuration file (e.g., `seo.py`):

```python
from seo_optimizer import register_metadata, MetadataField

@register_metadata
class BlogMetadata:
    title = MetadataField(max_length=70)
    description = MetadataField(max_length=160)
    keywords = KeywordsField()
    
    class Meta:
        use_cache = True
        use_sites = True
        use_i18n = True
```

### Template Integration

```html
{% load seo_tags %}

{% get_metadata as meta %}
<head>
    <title>{{ meta.title }}</title>
    <meta name="description" content="{{ meta.description }}">
    <meta name="keywords" content="{{ meta.keywords }}">
    {% if meta.og %}
        <meta property="og:title" content="{{ meta.og.title }}">
        <meta property="og:description" content="{{ meta.og.description }}">
    {% endif %}
</head>
```

## Examples

### Dynamic Metadata

```python
@register_metadata
class ProductMetadata:
    title = MetadataField(
        template="{{product.name}} - Buy Online | {{site.name}}"
    )
    description = MetadataField(
        template="Shop {{product.name}} starting at ${{product.price}}. {{product.short_description}}"
    )

    def get_context(self, request):
        return {
            'product': Product.objects.get(slug=request.path.split('/')[-1])
        }
```

### Multilingual SEO

```python
@register_metadata
class I18nMetadata:
    title = MetadataField()
    description = MetadataField()

    class Meta:
        use_i18n = True
        
    def get_translations(self, language):
        return {
            'title': {
                'en': 'Welcome to our store',
                'es': 'Bienvenido a nuestra tienda'
            },
            'description': {
                'en': 'Shop the best products online',
                'es': 'Compra los mejores productos en línea'
            }
        }
```

### Advanced URL Pattern Matching

```python
from seo_optimizer.models import RedirectPattern

# Redirect old blog URLs to new structure
RedirectPattern.objects.create(
    url_pattern="/blog/(\d{4})/(\d{2})/(.+)",
    redirect_url="/articles/$3",
    is_regex=True,
    status_code=301
)
```

## Best Practices

### Performance Optimization

1. **Enable Caching:**
   ```python
   class Meta:
       use_cache = True
       cache_timeout = 3600  # 1 hour
   ```

2. **Use Async Support** for high-traffic pages:
   ```python
   async def get_product_meta(request):
       return await ProductMetadata.async_get_metadata(request.path)
   ```

3. **Batch Process** metadata updates:
   ```python
   from seo_optimizer.utils import bulk_metadata_update
   
   await bulk_metadata_update(ProductMetadata, products)
   ```

### SEO Guidelines

1. **Title Length:** Keep titles between 50-60 characters
2. **Description Length:** Aim for 150-160 characters
3. **Keywords:** Use 5-8 relevant keywords
4. **Mobile Optimization:** Enable mobile-specific metadata
5. **URL Structure:** Use clean, descriptive URLs
6. **Sitemap:** Generate and update regularly

### Security

1. **Sanitize User Input:**
   ```python
   from seo_optimizer.utils import sanitize_meta
   
   title = sanitize_meta(user_input)
   ```

2. **API Keys:** Store sensitive data in environment variables
3. **Rate Limiting:** Enable for metadata API endpoints
4. **Access Control:** Restrict admin interface access

### Monitoring

1. **Enable Analytics:**
   ```python
   SEO_OPTIMIZER = {
       'ENABLE_ANALYTICS': True,
       'ANALYTICS_RETENTION': 90  # days
   }
   ```

2. **Track Performance:**
   ```python
   from seo_optimizer.analytics import track_meta_performance
   
   performance_data = await track_meta_performance('/products/')
   ```

3. **Set Up Alerts** for SEO issues and errors

## Contributing

We love your input! We want to make contributing to Django SEO Optimizer as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

### Development Process

1. Fork the repo and create your branch from `develop`
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Make your changes and add tests
4. Run tests and ensure they pass:
   ```bash
   pytest
   pytest --cov=seo_optimizer  # with coverage
   ```
5. Update documentation if needed
6. Submit a pull request

### Code Style

We use several tools to maintain code quality:

```bash
# Format code
black seo_optimizer

# Sort imports
isort seo_optimizer

# Check types
mypy seo_optimizer

# Run linter
flake8 seo_optimizer
```

### Commit Messages

Follow these guidelines:
- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests after the first line

For more detailed information about contributing, please see our [Contributing Guide](CONTRIBUTING.md).

## Documentation

For detailed documentation, visit [avixiii.com/django-seo-optimizer](https://avixiii.com/django-seo-optimizer)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Created and maintained by [avixiii](https://avixiii.com).

## Support

- Documentation: [avixiii.com/django-seo-optimizer](https://avixiii.com/django-seo-optimizer)
- Source Code: [github.com/avixiii-dev/django-seo-optimizer](https://github.com/avixiii-dev/django-seo-optimizer)
- Issue Tracker: [github.com/avixiii-dev/django-seo-optimizer/issues](https://github.com/avixiii-dev/django-seo-optimizer/issues)
