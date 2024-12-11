from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.conf import settings

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
    user_id = serializers.IntegerField(source='other_user_id')
    first_name = serializers.CharField(source='other_user_name')
    profile_image = serializers.SerializerMethodField()
    last_message = serializers.CharField(source='message')
    timestamp = serializers.DateTimeField()
    unread_count = serializers.SerializerMethodField()

    def get_unread_count(self, obj):
        user = self.context['request'].user
        return Message.objects.filter(
            receiver=user,
            sender_id=obj.other_user_id,
            read=False
        ).count()
    
    def get_profile_image(self, obj):
        profile_image = obj.other_user_profile_image
        if profile_image:
            return self.context['request'].build_absolute_uri(
                settings.MEDIA_URL +
                profile_image
            )
        return None

    class Meta:
        fields = ['user_id', 'first_name', 'profile_image', 'last_message', 'timestamp', 'unread_count']
        read_only_fields = fields