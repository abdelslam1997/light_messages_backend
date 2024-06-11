import pytest
from django.contrib.auth import get_user_model

from django.utils.translation import gettext_lazy as _

User = get_user_model()


@pytest.mark.django_db
def test_create_user():
    # Test creating a regular user
    email = "test@example.com"
    password = "password123"
    user = User.objects.create_user(email=email, password=password)
    assert user.email == email
    assert user.check_password(password)
    assert not user.is_staff
    assert not user.is_superuser

@pytest.mark.django_db
def test_create_superuser():
    # Test creating a superuser
    email = "admin@example.com"
    password = "admin123"
    user = User.objects.create_superuser(email=email, password=password)
    assert user.email == email
    assert user.check_password(password)
    assert user.is_staff
    assert user.is_superuser

@pytest.mark.django_db
def test_create_user_extra_fields():
    # Test creating a user with extra fields
    email = "test@example.com"
    password = "password123"
    first_name = "John"
    last_name = "Doe"
    user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
    assert user.email == email
    assert user.check_password(password)
    assert user.first_name == first_name
    assert user.last_name == last_name
    assert not user.is_staff
    assert not user.is_superuser

@pytest.mark.django_db
def test_create_superuser_extra_fields():
    # Test creating a superuser with extra fields
    email = "admin@example.com"
    password = "admin123"
    first_name = "Admin"
    last_name = "User"
    user = User.objects.create_superuser(email=email, password=password, first_name=first_name, last_name=last_name)
    assert user.email == email
    assert user.check_password(password)
    assert user.first_name == first_name
    assert user.last_name == last_name
    assert user.is_staff
    assert user.is_superuser

@pytest.mark.django_db
def test_with_no_email():
    # Test creating a user with no email
    with pytest.raises(ValueError, match=str(_("The Email field must be set"))):
        User.objects.create_user(email=None, password="password123")
