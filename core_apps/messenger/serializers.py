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
    user_id = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    last_message = serializers.CharField(source='message')
    timestamp = serializers.DateTimeField()
    unread_count = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context['request'].user

    def get_user_id(self, obj):
        return obj.get_other_user_id(self.user.id)
    
    def get_first_name(self, obj):
        return obj.get_other_user_first_name(self.user.id)
    
    def get_profile_image(self, obj):
        profile_image = obj.get_other_user_profile_image(self.user.id)
        if profile_image:
            return self.context['request'].build_absolute_uri(
                settings.MEDIA_URL +
                profile_image
            )
        return None
    
    def get_unread_count(self, obj):
        return Message.objects.filter(
            receiver=self.user,
            sender_id=obj.get_other_user_id(self.user.id),
            read=False
        ).count()

    class Meta:
        fields = ['user_id', 'first_name', 'profile_image', 'last_message', 'timestamp', 'unread_count']
        read_only_fields = fields