from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import Message


User = get_user_model()

class MessageCreateSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(
        slug_field='id',
        read_only=True
    )
    receiver = serializers.SlugRelatedField(
        slug_field='id',
        read_only=True
    )

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'message', 'timestamp', 'read']
        read_only_fields = ['id', 'sender', 'timestamp', 'read']


class MessageDetailSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(
        slug_field='id',
        read_only=True
    )
    receiver = serializers.SlugRelatedField(
        slug_field='id',
        read_only=True
    )

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'message', 'timestamp', 'read']
        read_only_fields = ['id', 'sender', 'receiver', 'timestamp', 'read']


class ConversationSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_message = serializers.CharField()
    profile_image = serializers.ImageField()
    timestamp = serializers.DateTimeField()

    class Meta:
        fields = ['user_id', 'first_name', 'last_message', 'profile_image', 'timestamp']
        read_only_fields = ['user_id', 'first_name', 'last_message', 'profile_image', 'timestamp']