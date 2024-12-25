"""
Custom exceptions for SEO Optimizer
Created by avixiii (https://avixiii.com)
"""

class MetadataValidationError(Exception):
    """Raised when metadata validation fails"""
    pass

class MetadataNotFoundError(Exception):
    """Raised when metadata is not found for a given path"""
    pass

class InvalidMetadataError(Exception):
    """Raised when metadata is invalid"""
    pass
