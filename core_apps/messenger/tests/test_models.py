import pytest
from django.contrib.auth import get_user_model
from core_apps.messenger.models import Message

User = get_user_model()

@pytest.mark.django_db
def test_message_creation(user):
    receiver = User.objects.create_user(email="receiver@example.com", password="password123")
    message = Message.objects.create(sender=user, receiver=receiver, message="Hello, World!")
    assert Message.objects.count() == 1
    assert message.sender == user
    assert message.receiver == receiver
    assert message.message == "Hello, World!"
    assert not message.read
