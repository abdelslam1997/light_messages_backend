import pytest
from django.contrib.auth import get_user_model
from core_apps.messenger.models import Message

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