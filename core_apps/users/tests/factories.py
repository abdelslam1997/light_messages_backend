import factory
from faker import Faker
from django.contrib.auth import get_user_model

User = get_user_model()

fake = Faker()

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyAttribute(lambda obj: fake.email())
    password = factory.PostGenerationMethodCall('set_password', 'password')
    first_name = factory.LazyAttribute(lambda obj: fake.first_name())
    last_name = factory.LazyAttribute(lambda obj: fake.last_name())


