import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from core_apps.messenger.models import Message

User = get_user_model()

@pytest.mark.django_db
class TestMessengerAPIs:
    def setup_method(self):
        self.client = APIClient()
        self.conversation_list_url = reverse("conversation-list-view")
        
    def create_test_message(self, sender, receiver, message="Test message"):
        return Message.objects.create(
            sender=sender,
            receiver=receiver,
            message=message
        )

    def test_conversation_list_unauthenticated(self):
        response = self.client.get(self.conversation_list_url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_conversation_list_authenticated(self, user, user_factory):
        # Create another user and some messages
        other_user = user_factory()
        self.create_test_message(user, other_user)
        self.create_test_message(other_user, user)

        # Authenticate and test
        self.client.force_authenticate(user=user)
        response = self.client.get(self.conversation_list_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1  # One conversation
        assert 'user_id' in response.data['results'][0]
        assert 'last_message' in response.data['results'][0]

    def test_message_list_create(self, user):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        
        conversation_url = reverse("conversation-list-create-view", kwargs={'user_id': other_user.id})
        
        # Test creating a message
        self.client.force_authenticate(user=user)
        message_data = {"message": "Hello, this is a test message"}
        response = self.client.post(conversation_url, message_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == message_data['message']
        assert response.data['sender'] == user.id
        assert response.data['receiver'] == other_user.id

        # Test listing messages
        response = self.client.get(conversation_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1

    def test_message_to_self(self, user):
        conversation_url = reverse("conversation-list-create-view", kwargs={'user_id': user.id})
        
        self.client.force_authenticate(user=user)
        message_data = {"message": "Test message to self"}
        response = self.client.post(conversation_url, message_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_message_read_status(self, user):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        
        # Create unread message
        message = self.create_test_message(other_user, user)
        assert not message.read

        # Access conversation should mark message as read
        conversation_url = reverse("conversation-list-create-view", kwargs={'user_id': other_user.id})
        self.client.force_authenticate(user=user)
        response = self.client.get(conversation_url)
        
        assert response.status_code == status.HTTP_200_OK
        message.refresh_from_db()
        assert message.read

    def test_long_message_validation(self, user):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        
        conversation_url = reverse("conversation-list-create-view", kwargs={'user_id': other_user.id})
        
        # Create message exceeding max length (2048 characters)
        self.client.force_authenticate(user=user)
        message_data = {"message": "x" * 2049}
        response = self.client.post(conversation_url, message_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_conversation_pagination(self, user):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        
        # Create multiple messages
        for i in range(15):  # Create more than default page size
            self.create_test_message(user, other_user, f"Message {i}")

        self.client.force_authenticate(user=user)
        response = self.client.get(self.conversation_list_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'results' in response.data

    def test_message_list_pagination(self, user):
        other_user = User.objects.create_user(
            email="other@example.com",
            password="testpass123"
        )
        conversation_url = reverse("conversation-list-create-view", kwargs={'user_id': other_user.id})
        
        # Create multiple messages
        for i in range(30):  # Create more than default page size
            self.create_test_message(user, other_user, f"Message {i}")

        self.client.force_authenticate(user=user)
        response = self.client.get(conversation_url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        assert len(response.data['results']) <= 25