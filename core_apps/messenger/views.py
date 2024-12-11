from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from channels.layers import get_channel_layer

from django.db.models import (
    Q, F, Case, 
    When, IntegerField, OuterRef, 
    Subquery, CharField
)
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.conf import settings

from .models import Message
from .serializers import (
    MessageCreateSerializer,
    MessageDetailSerializer, 
    ConversationSerializer
)
from .paginations import (
    RecentConversationsPagination,
    ConversationMessagesPagination
)

from asgiref.sync import async_to_sync


User = get_user_model()

class ConversationMessageListCreateView(generics.ListCreateAPIView):
    ''' List or Create messages View ( for a specific conversation ) '''
    serializer_class = MessageCreateSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ConversationMessagesPagination

    def get_queryset(self):
        user = self.request.user
        other_user_id = self.kwargs.get('user_id')
        return Message.objects.filter(
            Q(sender=user, receiver_id=other_user_id) | Q(sender_id=other_user_id, receiver=user)
        ).order_by('-timestamp')

    def perform_create(self, serializer):
        receiver_id = self.kwargs.get('user_id')
        receiver = get_object_or_404(User, id=receiver_id)
        # Validate if the receiver is not the same as the sender
        if receiver.id == self.request.user.id:
            raise ValidationError({
                'receiver': [_('You cannot send a message to yourself.'),]
            })
        
        message = serializer.save(sender=self.request.user, receiver=receiver)
        # Get channel layer
        channel_layer = get_channel_layer()
        # Send notification to receiver's group
        receiver_group_name = f"user_{receiver_id}"
        # Prepare message data
        message_data = {
            'type': 'new_message',
            'message': {
                'id': message.id,
                'sender': message.sender.id,
                'message': message.message,
                'timestamp': message.timestamp.isoformat(),
            }
        }
        # Send to receiver's group
        async_to_sync(channel_layer.group_send)(
            receiver_group_name,
            message_data
        )

    def list(self, request, *args, **kwargs):
        # Mark all previous messages as read
        self.get_queryset().update(read=True)
        # Get the paginated queryset
        queryset = self.paginate_queryset(self.get_queryset())
        serializer = MessageDetailSerializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)


class ConversationListView(generics.ListAPIView):
    ''' List recent conversations View '''
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = RecentConversationsPagination

    def get_queryset(self):
        user = self.request.user
        messages = Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).annotate(
            other_user_id=Case(
                When(sender=user, then=F('receiver_id')),
                default=F('sender_id'),
                output_field=IntegerField()
            ),
            other_user_name=Case(
                When(sender=user, then=F('receiver__first_name')),
                default=F('sender__first_name'),
                output_field=CharField()
            ),
            other_user_profile_image=Case(
                When(sender=user, then=F('receiver__profile_image')),
                default=F('sender__profile_image'),
                output_field=CharField()
            ),
        ).order_by('-timestamp')

        subquery = messages.filter(
            other_user_id=OuterRef('other_user_id')
        ).order_by('-id').values('id')[:1]

        queryset = messages.filter(
            id=Subquery(subquery)
        )
        ### TODO: Add Analytics after adding the loggers in settings.py
        ### Uncomment the following if you want to see actual SQL query
        print(queryset.query)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.paginate_queryset(self.get_queryset())
        chat_data = []
        user = self.request.user
        for message in queryset:
            profile_image_url = request.build_absolute_uri(
                settings.MEDIA_URL + message.other_user_profile_image
            )
            chat_data.append({
                'user_id': message.other_user_id,
                'first_name': message.other_user_name,
                'profile_image': profile_image_url,
                'last_message': message.message,
                'timestamp': message.timestamp,
                'unread_count': Message.objects.filter(
                    receiver=user,
                    sender_id=message.other_user_id,
                    read=False
                ).count()
            })
        return self.get_paginated_response(chat_data)
