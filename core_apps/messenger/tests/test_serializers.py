import pytest
from django.test import RequestFactory
from django.conf import settings

from core_apps.messenger.serializers import (
    MessageCreateSerializer,
    MessageDetailSerializer,
    ConversationSerializer
)
from core_apps.messenger.models import Message


@pytest.mark.django_db
class TestMessageCreateSerializer:
    def test_serializer_with_valid_data(self, user, user_factory):
        receiver = user_factory()
        message = Message.objects.create(
            sender=user,
            receiver=receiver,
            message="Test message"
        )
        serializer = MessageCreateSerializer(message)
        
        assert serializer.data['sender'] == user.id
        assert serializer.data['receiver'] == receiver.id
        assert serializer.data['message'] == "Test message"
        assert 'timestamp' in serializer.data
        assert 'read' in serializer.data

    def test_serializer_validation(self):
        serializer = MessageCreateSerializer(data={
            'message': 'x' * 2049  # Exceeds max_length
        })
        assert not serializer.is_valid()
        assert 'message' in serializer.errors


@pytest.mark.django_db
class TestMessageDetailSerializer:
    def test_serializer_with_valid_data(self, user, user_factory):
        receiver = user_factory()
        message = Message.objects.create(
            sender=user,
            receiver=receiver,
            message="Test message"
        )
        serializer = MessageDetailSerializer(message)
        
        assert serializer.data['sender'] == user.id
        assert serializer.data['receiver'] == receiver.id
        assert serializer.data['message'] == "Test message"
        assert not serializer.data['read']

    def test_read_only_fields(self, user, user_factory):
        receiver = user_factory()
        message = Message.objects.create(
            sender=user,
            receiver=receiver,
            message="Test message"
        )
        
        # Attempt to modify read-only fields
        serializer = MessageDetailSerializer(message, data={
            'sender': receiver.id,  # Should not change
            'receiver': user.id,    # Should not change
            'message': "Updated message",
            'read': True           # Should not change
        })
        
        # Validate serializer and check if read-only fields are ignored
        serializer.is_valid() # Will return True, but will ignore read-only fields

        assert 'sender' not in serializer.validated_data
        assert 'receiver' not in serializer.validated_data
        assert 'read' not in serializer.validated_data


@pytest.mark.django_db
class TestConversationSerializer:
    def setup_method(self):
        self.factory = RequestFactory()
        self.request = self.factory.get('/')

    def test_conversation_serialization(self, user, user_factory, mock_request):
        other_user = user_factory(
            first_name="Test",
            profile_image="profiles/test.jpg"
        )
        
        # Create a message for the conversation
        message = Message.objects.create(
            sender=other_user,
            receiver=user,
            message="Test conversation message"
        )
        
        # Mock the request context
        context = {'request': mock_request(user)}
        
        # Create a conversation object with required attributes
        conversation_data = {
            'other_user_id': other_user.id,
            'other_user_name': other_user.first_name,
            'other_user_profile_image': other_user.profile_image.url,
            'message': message.message,
            'timestamp': message.timestamp
        }
        
        # Convert dict to object for serializer
        conversation_obj = type('ConversationObj', (), conversation_data)
        
        serializer = ConversationSerializer(
            conversation_obj,
            context=context
        )
        
        assert serializer.data['user_id'] == other_user.id
        assert serializer.data['first_name'] == "Test"
        assert serializer.data['last_message'] == "Test conversation message"
        assert 'timestamp' in serializer.data
        assert 'unread_count' in serializer.data

    def test_profile_image_url(self, user_factory, mock_request):
        other_user = user_factory(
            profile_image="profiles/test.jpg"
        )
        
        conversation_data = {
            'other_user_id': other_user.id,
            'other_user_name': other_user.first_name,
            'other_user_profile_image': other_user.profile_image.url,
            'message': "Test message",
            'timestamp': "2024-01-01T00:00:00Z"
        }
        conversation_obj = type('ConversationObj', (), conversation_data)
        
        # Mock the request context
        context = {'request': mock_request()}
        serializer = ConversationSerializer(
            conversation_obj,
            context=context
        )
        
        expected_url = self.request.build_absolute_uri(
            settings.MEDIA_URL + other_user.profile_image.url
        )
        assert serializer.data['profile_image'] == expected_url

    def test_unread_count(self, user, user_factory):
        other_user = user_factory()
        
        # Create multiple unread messages
        for _ in range(3):
            Message.objects.create(
                sender=other_user,
                receiver=user,
                message="Test message",
                read=False
            )
        
        # Create a read message
        Message.objects.create(
            sender=other_user,
            receiver=user,
            message="Read message",
            read=True
        )
        
        conversation_data = {
            'other_user_id': other_user.id,
            'other_user_name': other_user.first_name,
            'other_user_profile_image': None,
            'message': "Test message",
            'timestamp': "2024-01-01T00:00:00Z"
        }
        conversation_obj = type('ConversationObj', (), conversation_data)
        
        context = {
            'request': self.request
        }
        self.request.user = user
        
        serializer = ConversationSerializer(
            conversation_obj,
            context=context
        )
        
        assert serializer.data['unread_count'] == 3
