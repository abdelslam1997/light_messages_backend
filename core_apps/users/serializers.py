from rest_framework.serializers import ModelSerializer, CharField, ValidationError
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from .exceptions import DuplicatedEmailException

User = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
        read_only_fields = ("id", "email", "date_joined", "is_active", "is_staff")


class UserRegistrationSerializer(ModelSerializer):
    first_name = CharField(max_length=30)
    last_name = CharField(max_length=30)

    password = CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "profile_image",
        ]

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise DuplicatedEmailException()
        return email

    def validate_first_name(self, first_name):
        if not first_name:
            raise ValidationError(_("First Name is required"))
        return first_name

    def validate_last_name(self, last_name):
        if not last_name:
            raise ValidationError(_("Last Name is required"))
        return last_name

    def create(self, validated_data):

        user = User(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            profile_image=validated_data.get("profile_image"),
        )
        user.set_password(validated_data["password"])
        user.save()
        return user
