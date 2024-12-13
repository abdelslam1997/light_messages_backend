import factory

from django.contrib.auth import get_user_model

from core_apps.users.tests.factories import UserFactory
from core_apps.messenger.models import Message


User = get_user_model()

class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    sender = factory.SubFactory(UserFactory)
    receiver = factory.SubFactory(UserFactory)
    message = "Hello, World!"
