import pytest
from django.contrib.auth import get_user_model

from core_apps.messenger.models import Message, Conversation
from core_apps.messenger.utils.conversations import get_conversation_id

User = get_user_model()


# ── Message model tests ─────────────────────────────────────────

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
        Message.objects.create(
            sender=user,
            receiver=user,
            message="Hello, world!"
        )
    assert "different_sender_receiver_constraint" in str(e.value)


def test_message_can_not_exceed_2048_characters(db, user_factory):
    user = user_factory()
    user2 = user_factory()
    long_text = "a" * 2049

    with pytest.raises(Exception) as e:
        Message.objects.create(
            sender=user,
            receiver=user2,
            message=long_text
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
    # Reversed direction should produce the same conversation_id
    reverse_message = Message.objects.create(
        sender=receiver,
        receiver=sender,
        message="Reply message"
    )
    assert reverse_message.conversation_id == expected_id


def test_message_database_indexes(db):
    indexes = {idx.name: idx for idx in Message._meta.indexes}
    assert "conversation_timestamp_idx" in indexes
    conv_idx = indexes["conversation_timestamp_idx"]
    assert conv_idx.fields == ["conversation_id", "-timestamp"]


def test_message_model_meta_options(db):
    meta = Message._meta
    assert meta.ordering == ["-timestamp"]
    assert meta.verbose_name == "Message"
    assert meta.verbose_name_plural == "Messages"
    constraint = meta.constraints[0]
    assert constraint.name == "different_sender_receiver_constraint"


# ── Conversation model tests ────────────────────────────────────

def test_conversation_created_on_message(db, user_factory):
    """Saving a Message should auto-create a Conversation row."""
    sender = user_factory()
    receiver = user_factory()
    Message.objects.create(sender=sender, receiver=receiver, message="hi")

    conv = Conversation.objects.get(
        conversation_id=get_conversation_id(sender.id, receiver.id)
    )
    assert conv.last_message_text == "hi"
    assert conv.participant_1_id == min(sender.id, receiver.id)
    assert conv.participant_2_id == max(sender.id, receiver.id)


def test_conversation_updated_on_second_message(db, user_factory):
    sender = user_factory()
    receiver = user_factory()
    Message.objects.create(sender=sender, receiver=receiver, message="first")
    msg2 = Message.objects.create(sender=receiver, receiver=sender, message="second")

    conv = Conversation.objects.get(
        conversation_id=get_conversation_id(sender.id, receiver.id)
    )
    assert conv.last_message_text == "second"
    assert conv.last_message_id == msg2.id


def test_conversation_unread_count_increments(db, user_factory):
    sender = user_factory()
    receiver = user_factory()
    Message.objects.create(sender=sender, receiver=receiver, message="m1")
    Message.objects.create(sender=sender, receiver=receiver, message="m2")

    conv = Conversation.objects.get(
        conversation_id=get_conversation_id(sender.id, receiver.id)
    )
    # receiver should have 2 unread
    assert conv.get_unread_count(receiver.id) == 2
    # sender should have 0 unread
    assert conv.get_unread_count(sender.id) == 0


def test_conversation_get_other_user_id(db, user_factory):
    sender = user_factory()
    receiver = user_factory()
    Message.objects.create(sender=sender, receiver=receiver, message="hi")
    conv = Conversation.objects.get(
        conversation_id=get_conversation_id(sender.id, receiver.id)
    )
    assert conv.get_other_user_id(sender.id) == receiver.id
    assert conv.get_other_user_id(receiver.id) == sender.id


def test_conversation_str(db, user_factory):
    sender = user_factory()
    receiver = user_factory()
    Message.objects.create(sender=sender, receiver=receiver, message="hi")
    conv = Conversation.objects.get(
        conversation_id=get_conversation_id(sender.id, receiver.id)
    )
    assert str(conv) == conv.conversation_id