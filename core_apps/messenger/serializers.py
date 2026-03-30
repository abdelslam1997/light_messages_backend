from rest_framework import serializers

from django.contrib.auth import get_user_model

from .models import Message, Conversation


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
    sender = serializers.SerializerMethodField()
    receiver = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'message', 'timestamp', 'read']
        read_only_fields = ['id', 'sender', 'receiver', 'timestamp', 'read']

    def get_sender(self, obj):
        return obj.sender_id
    
    def get_receiver(self, obj):
        return obj.receiver_id


class ConversationSerializer(serializers.ModelSerializer):
    user_id = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()
    last_message = serializers.CharField(source='last_message_text')
    timestamp = serializers.DateTimeField(source='last_message_timestamp')
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['user_id', 'first_name', 'profile_image', 'last_message', 'timestamp', 'unread_count']
        read_only_fields = fields

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context['request'].user

    def get_user_id(self, obj):
        return obj.get_other_user_id(self.user.id)

    def get_first_name(self, obj):
        other, _ = obj.get_other_user(self.user.id)
        return other.first_name

    def get_profile_image(self, obj):
        other, _ = obj.get_other_user(self.user.id)
        if other.profile_image:
            return self.context['request'].build_absolute_uri(other.profile_image.url)
        return None

    def get_unread_count(self, obj):
        return obj.get_unread_count(self.user.id)