import pytest
from pytest_factoryboy import register

from django.test import RequestFactory
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

from core_apps.users.tests.factories import UserFactory


register(UserFactory)

@pytest.fixture
def user(db, user_factory):
    return user_factory()


@pytest.fixture
def mock_request():
    def create_mock_request(user=None):
        request = RequestFactory().get('/')
        
        # Add session middleware
        session_middleware = SessionMiddleware(get_response=lambda r: None)
        session_middleware.process_request(request)
        request.session.save()

        # Add auth middleware
        auth_middleware = AuthenticationMiddleware(get_response=lambda r: None)
        auth_middleware.process_request(request)

        # Set user explicitly
        request.user = user

        # Add build_absolute_uri method
        if not hasattr(request, 'build_absolute_uri'):
            request.build_absolute_uri = lambda x: f'http://testserver{x}'

        return request
    return create_mock_request