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