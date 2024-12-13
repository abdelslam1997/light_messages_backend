import pytest
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

@pytest.mark.django_db
class TestUserManager:
    def test_create_user(self, user_factory):
        user = user_factory()
        assert user.email
        assert user.check_password('password')  # default password from factory
        assert not user.is_staff
        assert not user.is_superuser
        assert user.is_active

    def test_create_user_with_custom_email(self, user_factory):
        email = "testuser@example.com"
        user = user_factory(email=email)
        assert user.email == email

    def test_create_superuser(self, user_factory):
        user = user_factory(is_staff=True, is_superuser=True)
        assert user.is_staff
        assert user.is_superuser
        assert user.is_active
