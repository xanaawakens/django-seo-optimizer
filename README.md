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

## Documentation

For detailed documentation, visit [avixiii.com/django-seo-optimizer](https://avixiii.com/django-seo-optimizer)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Created and maintained by [avixiii](https://avixiii.com).

## Support

- Documentation: [avixiii.com/django-seo-optimizer](https://avixiii.com/django-seo-optimizer)
- Source Code: [github.com/avixiii-dev/django-seo-optimizer](https://github.com/avixiii-dev/django-seo-optimizer)
- Issue Tracker: [github.com/avixiii-dev/django-seo-optimizer/issues](https://github.com/avixiii-dev/django-seo-optimizer/issues)
