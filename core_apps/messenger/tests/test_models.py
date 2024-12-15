import pytest
from django.contrib.auth import get_user_model
from django.db import connection
from django.db.models import Index

from core_apps.messenger.models import Message
from core_apps.messenger.utils.conversations import get_conversation_id

User = get_user_model()


def test_message_creation(db, user_factory):
    user = user_factory()
    user2 = user_factory()
    message = Message.objects.create(
        sender=user,
        receiver=user2,
        message="Hello, world!"
    )
    assert message.sender == user
    assert message.receiver == user2
    assert message.message == "Hello, world!"
    assert message.read is False
    assert message.timestamp is not None
    assert str(message) == "Hello, world!"


def test_message_creation_same_sender_and_receiver(db, user_factory):
    user = user_factory()
    with pytest.raises(Exception) as e:
        message = Message.objects.create(
            sender=user,
            receiver=user,
            message="Hello, world!"
        )
    assert "different_sender_receiver_constraint" in str(e.value)


def test_message_can_not_exceed_2048_characters(db, user_factory):
    user = user_factory()
    user2 = user_factory()
    message = "a" * 2049

    with pytest.raises(Exception) as e:
        message = Message.objects.create(
            sender=user,
            receiver=user2,
            message=message
        )
    assert "2048" in str(e.value)


def test_conversation_id_generation(db, user_factory):
    sender = user_factory()
    receiver = user_factory()
    message = Message.objects.create(
        sender=sender,
        receiver=receiver,
        message="Test message"
    )
    
    expected_id = get_conversation_id(sender.id, receiver.id)
    assert message.conversation_id == expected_id
    # Test if conversation_id remains same for reversed users
    reverse_message = Message.objects.create(
        sender=receiver,
        receiver=sender,
        message="Reply message"
    )
    assert reverse_message.conversation_id == expected_id

def test_get_other_user_methods(db, user_factory):
    sender = user_factory(
        first_name="John",
        profile_image="profiles/john.jpg"
    )
    receiver = user_factory(
        first_name="Jane",
        profile_image="profiles/jane.jpg"
    )
    message = Message.objects.create(
        sender=sender,
        receiver=receiver,
        message="Test message"
    )
    
    # Test from sender's perspective
    assert message.get_other_user_id(sender.id) == receiver.id
    assert message.get_other_user_first_name(sender.id) == "Jane"
    assert message.get_other_user_profile_image(sender.id) == receiver.profile_image.url
    
    # Test from receiver's perspective
    assert message.get_other_user_id(receiver.id) == sender.id
    assert message.get_other_user_first_name(receiver.id) == "John"
    assert message.get_other_user_profile_image(receiver.id) == sender.profile_image.url

def test_get_other_user_profile_image_null(db, user_factory):
    sender = user_factory(profile_image=None)
    receiver = user_factory(profile_image=None)
    message = Message.objects.create(
        sender=sender,
        receiver=receiver,
        message="Test message"
    )
    
    assert message.get_other_user_profile_image(sender.id) is None
    assert message.get_other_user_profile_image(receiver.id) is None

def test_database_indexes(db):
    indexes = {
        idx.name: idx for idx in Message._meta.indexes
    }
    
    # Test conversation timestamp index
    assert "conversation_timestamp_idx" in indexes
    conv_idx = indexes["conversation_timestamp_idx"]
    assert conv_idx.fields == ["conversation_id", "timestamp"]
    
    # Test sender read timestamp index
    assert "sender_read_timestamp_idx" in indexes
    read_idx = indexes["sender_read_timestamp_idx"]
    assert read_idx.fields == ["sender", "read", "timestamp"]

def test_model_meta_options(db):
    meta = Message._meta
    assert meta.ordering == ["-timestamp"]
    assert meta.verbose_name == "Message"
    assert meta.verbose_name_plural == "Messages"
    
    # Test constraint
    constraint = meta.constraints[0]
    assert constraint.name == "different_sender_receiver_constraint"