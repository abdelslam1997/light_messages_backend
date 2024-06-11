import pytest
from pytest_factoryboy import register

from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.middleware import AuthenticationMiddleware

from core_apps.users.tests.factories import UserFactory


register(UserFactory)

@pytest.fixture
def user(db, user_factory):
    return user_factory()




@pytest.fixture
def mock_request():
    def middleware(request):
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        middleware = AuthenticationMiddleware(lambda req: None)
        middleware.process_request(request)

        return request

    return middleware(RequestFactory().get("/"))
