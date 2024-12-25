"""
Pytest configuration file
Created by avixiii (https://avixiii.com)
"""
import pytest
from django.conf import settings
from django.test import RequestFactory
from django.contrib.auth import get_user_model
import factory


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')


@pytest.fixture
def user_factory():
    return UserFactory


@pytest.fixture
def request_factory():
    return RequestFactory()


@pytest.fixture
def mock_html_content():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Page</title>
        <meta name="description" content="Test description">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            @media (max-width: 768px) {
                body { font-size: 16px; }
            }
        </style>
    </head>
    <body>
        <h1>Test Content</h1>
        <img src="test.jpg" srcset="test-small.jpg 300w, test-large.jpg 600w">
        <a href="#" style="font-size: 16px">Test Link</a>
    </body>
    </html>
    """
