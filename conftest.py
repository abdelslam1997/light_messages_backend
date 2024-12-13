import pytest
from pytest_factoryboy import register

from core_apps.users.tests.factories import UserFactory


register(UserFactory)

@pytest.fixture
def user(db, user_factory):
    return user_factory()