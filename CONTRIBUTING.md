# Contributing to Django SEO Optimizer

First off, thank you for considering contributing to Django SEO Optimizer! It's people like you that make Django SEO Optimizer such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the issue list as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include details about your configuration and environment

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful

### Pull Requests

* Fill in the required template
* Do not include issue numbers in the PR title
* Follow the Python style guide
* Include thoughtfully-worded, well-structured tests
* Document new code
* End all files with a newline

## Development Process

1. Fork the repo and create your branch from `develop`
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests to ensure everything is working:
   ```bash
   pytest
   ```
4. Make your changes and add tests
5. Run the test suite again
6. Push to your fork and submit a pull request

## Testing

We use pytest for our test suite. To run tests:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_fields.py

# Run with coverage report
pytest --cov=seo_optimizer
```

### Writing Tests

* Write test docstrings
* Each test should have a single assertion
* Use descriptive test names
* Follow the Arrange-Act-Assert pattern

Example:
```python
def test_metadata_field_validates_max_length():
    """Test that MetadataField correctly validates max_length."""
    # Arrange
    field = MetadataField(max_length=10)
    
    # Act & Assert
    with pytest.raises(ValidationError):
        field.clean("This is too long")
```

## Style Guide

We follow PEP 8 with some modifications:

* Line length limit is 100 characters
* Use double quotes for strings
* Use trailing commas in multi-line structures
* Sort imports using isort

Use black for code formatting:
```bash
black seo_optimizer
```

## Documentation

* Use Google-style docstrings
* Update the README.md if needed
* Add docstrings to all public methods
* Include code examples in docstrings
* Update type hints

Example:
```python
def get_metadata(
    self,
    path: str,
    language: Optional[str] = None
) -> Dict[str, Any]:
    """Get metadata for the given path and language.
    
    Args:
        path: The URL path to get metadata for
        language: Optional language code (e.g., 'en', 'es')
        
    Returns:
        Dictionary containing metadata fields
        
    Example:
        >>> meta = MetadataManager().get_metadata('/products/')
        >>> print(meta['title'])
        'Our Products'
    """
```

## Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

Example:
```
Add async support for metadata retrieval

- Implement AsyncMetadataManager
- Add async_get_metadata method
- Update documentation with async examples

Fixes #123
```

## Release Process

1. Update version in `seo_optimizer/version.py`
2. Update CHANGELOG.md
3. Create release notes
4. Tag the release
5. Push to PyPI

## Questions?

Feel free to contact the project maintainers if you have any questions or need help with the contribution process.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
