from rest_framework import serializers
from .models import Message
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(
        slug_field='id',
        read_only=True
    )
    receiver = serializers.SlugRelatedField(
        slug_field='id',
        queryset=User.objects.all()
    )

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'message', 'timestamp', 'read']
        read_only_fields = ['id', 'sender', 'timestamp', 'read']



class ChatSummarySerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_message = serializers.CharField()
    profile_image = serializers.ImageField()
    timestamp = serializers.DateTimeField()


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