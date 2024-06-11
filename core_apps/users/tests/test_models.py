import pytest

from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@pytest.mark.django_db
def test_user_creation(user):
    assert User.objects.count() == 1
    assert User.objects.first() == user


@pytest.mark.django_db
def test_get_full_name(user):
    assert user.get_full_name() == f"{user.first_name} {user.last_name}"


@pytest.mark.django_db
def test_get_short_name(user):
    assert user.get_short_name() == user.first_name


@pytest.mark.django_db
def test_str(user):
    assert str(user) == user.email