import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
class TestUserAPIs:
    def setup_method(self):
        self.client = APIClient()
        self.registration_url = reverse("user-registration")
        self.token_obtain_url = reverse("token_obtain_pair")
        self.token_refresh_url = reverse("token_refresh")
        self.token_verify_url = reverse("token_verify")
        self.user_retrieve_url = reverse("user-retrieve")
        self.user_search_url = reverse("user-search")

    def test_user_registration_success(self):
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
        response = self.client.post(self.registration_url, payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=payload["email"]).exists()
        assert "password" not in response.data

    def test_user_registration_invalid_data(self):
        # Test with invalid email
        payload = {
            "email": "invalid-email",
            "password": "testpass123",
        }
        response = self.client.post(self.registration_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.django_db
    def test_token_obtain(self, user):
        payload = {
            "email": user.email,
            "password": "password",  # Set in UserFactory
        }
        response = self.client.post(self.token_obtain_url, payload)
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_token_refresh(self, user):
        # First obtain tokens
        tokens = self.client.post(
            self.token_obtain_url,
            {"email": user.email, "password": "password"}
        ).data
        
        # Test refresh
        response = self.client.post(
            self.token_refresh_url,
            {"refresh": tokens["refresh"]}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data

    def test_token_verify(self, user):
        # First obtain tokens
        tokens = self.client.post(
            self.token_obtain_url,
            {"email": user.email, "password": "password"}
        ).data
        
        # Verify token
        response = self.client.post(
            self.token_verify_url,
            {"token": tokens["access"]}
        )
        assert response.status_code == status.HTTP_200_OK

    def test_user_retrieve(self, user):
        self.client.force_authenticate(user=user)
        response = self.client.get(self.user_retrieve_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_user_retrieve_unauthorized(self):
        response = self.client.get(self.user_retrieve_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.django_db
    def test_user_search(self, user):
        self.client.force_authenticate(user=user)
        
        # Create some test users
        User.objects.create_user(
            email="searchtest1@example.com",
            password="testpass123"
        )
        User.objects.create_user(
            email="searchtest2@example.com",
            password="testpass123"
        )

        # Test search with valid query
        response = self.client.get(f"{self.user_search_url}?query=searchtest")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        # Test search with short query
        response = self.client.get(f"{self.user_search_url}?query=te")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

        # Test search without query
        response = self.client.get(self.user_search_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0
