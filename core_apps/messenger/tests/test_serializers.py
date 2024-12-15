import pytest
from django.test import RequestFactory
from django.conf import settings
from django.db.utils import IntegrityError

from core_apps.messenger.serializers import (
    MessageCreateSerializer,
    MessageDetailSerializer,
    ConversationSerializer
)
from core_apps.messenger.models import Message
from core_apps.messenger.utils.conversations import get_conversation_id


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

    def test_conversation_id_generation(self, user, user_factory):
        receiver = user_factory()
        data = {
            'message': 'Test message'
        }
        
        serializer = MessageCreateSerializer(data=data)
        assert serializer.is_valid()
        
        message = serializer.save(sender=user, receiver=receiver)
        expected_conversation_id = get_conversation_id(user.id, receiver.id)
        assert message.conversation_id == expected_conversation_id

    def test_same_sender_receiver_validation(self, user):
        data = {
            'message': 'Test message'
        }
        
        serializer = MessageCreateSerializer(data=data)
        assert serializer.is_valid()
        
        with pytest.raises(IntegrityError) as exc_info:
            serializer.save(sender=user, receiver=user)
        assert "different_sender_receiver_constraint" in str(exc_info.value)


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

    def test_conversation_id_field(self, user, user_factory):
        receiver = user_factory()
        message = Message.objects.create(
            sender=user,
            receiver=receiver,
            message="Test message"
        )
        serializer = MessageDetailSerializer(message)
        
        expected_conversation_id = get_conversation_id(user.id, receiver.id)
        assert message.conversation_id == expected_conversation_id
        assert 'conversation_id' not in serializer.data  # Should not be exposed


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
        
        message = Message.objects.create(
            sender=other_user,
            receiver=user,
            message="Test conversation message"
        )
        
        context = {'request': mock_request(user)}
        serializer = ConversationSerializer(message, context=context)
        
        assert serializer.data['user_id'] == other_user.id
        assert serializer.data['first_name'] == "Test"
        assert serializer.data['last_message'] == "Test conversation message"
        assert 'timestamp' in serializer.data
        assert 'unread_count' in serializer.data

    def test_profile_image_url(self, user, user_factory, mock_request):
        other_user = user_factory(profile_image="profiles/test.jpg")
        message = Message.objects.create(
            sender=other_user,
            receiver=user,
            message="Test message"
        )
        
        context = {'request': mock_request(user)}
        serializer = ConversationSerializer(message, context=context)
        
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
        
        last_message = Message.objects.create(
            sender=other_user,
            receiver=user,
            message="Last message",
            read=True
        )
        
        context = {'request': self.request}
        self.request.user = user
        serializer = ConversationSerializer(last_message, context=context)
        assert serializer.data['unread_count'] == 3

    def test_conversation_fields_with_indexes(self, user, user_factory, mock_request):
        other_user = user_factory(
            first_name="Test",
            profile_image="profiles/test.jpg"
        )
        
        Message.objects.create(
            sender=other_user,
            receiver=user,
            message="First message",
            read=True
        )
        
        last_message = Message.objects.create(
            sender=other_user,
            receiver=user,
            message="Second message",
            read=False
        )
        
        context = {'request': mock_request(user)}
        serializer = ConversationSerializer(last_message, context=context)
        
        assert serializer.data['last_message'] == "Second message"
        assert serializer.data['unread_count'] == 1
        assert serializer.data['timestamp'] == last_message.timestamp.isoformat().replace('+00:00', 'Z')

    def test_conversation_with_deleted_user(self, user, user_factory, mock_request):
        other_user = user_factory(first_name="", profile_image=None)
        message = Message.objects.create(
            sender=other_user,
            receiver=user,
            message="Test message"
        )
        
        context = {'request': mock_request(user)}
        serializer = ConversationSerializer(message, context=context)
        
        assert serializer.data['first_name'] == ""
        assert serializer.data['profile_image'] is None
