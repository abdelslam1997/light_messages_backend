import pytest
from rest_framework.exceptions import ValidationError

from django.core.files.uploadedfile import SimpleUploadedFile

from core_apps.users.serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserSearchSerializer
)


@pytest.mark.django_db
class TestUserSerializer:
    def test_serializer_contains_expected_fields(self, user):
        serializer = UserSerializer(user)
        expected_fields = {
            "id", "email", "first_name", "last_name", 
            "date_joined", "profile_image"
        }
        assert set(serializer.data.keys()) == expected_fields

    def test_profile_image_url_with_request(self, user, mock_request):
        request = mock_request(user)
        serializer = UserSerializer(user, context={'request': request})
        
        if user.profile_image:
            assert serializer.data['profile_image'].startswith('http://testserver')
        else:
            assert serializer.data['profile_image'] is None


@pytest.mark.django_db
class TestUserRegistrationSerializer:
    def test_valid_registration_data(self):
        data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123"
        }
        serializer = UserRegistrationSerializer(data=data)
        assert serializer.is_valid()

    def test_duplicate_email_registration(self, user):
        data = {
            "email": user.email,  # Using existing user's email
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123"
        }
        serializer = UserRegistrationSerializer(data=data)
        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)
        
        # Assert that the error message is as expected
        assert "email" in serializer.errors
        assert "unique" in serializer.errors["email"][0].code

    def test_missing_required_fields(self):
        data = {
            "email": "test@example.com",
            "password": "testpass123"
            # Missing first_name and last_name
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        assert "first_name" in serializer.errors
        assert "last_name" in serializer.errors

    def test_creates_user_with_profile_image(self, mock_image_file):
        image_file = mock_image_file(
            size=(100, 100), color='red', format='JPEG'
        )
        # Create a user with profile image
        data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
            "profile_image": image_file
        }
        # Validate the data
        serializer = UserRegistrationSerializer(data=data)
        serializer.is_valid()
        assert serializer.is_valid()
        # Check that the profile image is saved
        user = serializer.save()
        assert user.profile_image is not None

    def test_invalid_profile_image(self):
        # Test invalid image type
        invalid_file = SimpleUploadedFile(
            "test.txt",
            b"invalid file content",
            content_type="text/plain"
        )
        data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
            "profile_image": invalid_file
        }
        serializer = UserRegistrationSerializer(data=data)
        assert not serializer.is_valid()
        errors = serializer.errors
        assert "profile_image" in errors
        assert "invalid_image" in errors["profile_image"][0].code

    def test_profile_image_size_limit(self, mock_image_file):
        oversized_file = mock_image_file(
            size=(1024, 1024), 
            override_file_size=6 * 1024 * 1024
        )
        data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
            "profile_image": oversized_file
        }
        serializer = UserRegistrationSerializer(data=data)

        with pytest.raises(ValidationError):
            serializer.is_valid(raise_exception=True)

        errors = serializer.errors
        assert "profile_image" in errors
        assert "exceeded_size_limit" in errors["profile_image"][0].code


@pytest.mark.django_db
class TestUserSearchSerializer:
    def test_serializer_contains_expected_fields(self, user):
        serializer = UserSearchSerializer(user)
        expected_fields = {
            "id", "email", "first_name", "last_name", "profile_image"
        }
        assert set(serializer.data.keys()) == expected_fields

    def test_profile_image_url_with_request(self, user, mock_request):
        request = mock_request(user)
        serializer = UserSearchSerializer(user, context={'request': request})
        
        if user.profile_image:
            assert serializer.data['profile_image'].startswith('http://testserver')
        else:
            assert serializer.data['profile_image'] is None

    def test_read_only_fields(self, user, mock_request):
        request = mock_request(user)
        serializer = UserSearchSerializer(
            user,
            context={'request': request},
            data={'first_name': 'Changed'}
        )
        assert serializer.is_valid()
        # Should not update any fields as they are read-only
        serializer.save()
        user.refresh_from_db()
        assert user.first_name != 'Changed'
