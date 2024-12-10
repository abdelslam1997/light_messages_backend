from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from django.db.models import (
    Q, F, Case, 
    When, IntegerField, OuterRef, 
    Subquery, CharField
)
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from django.conf import settings

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Message
from .serializers import (
    MessageCreateSerializer,
    MessageDetailSerializer, 
    ConversationSerializer
)


User = get_user_model()

class ConversationMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        other_user_id = self.kwargs.get('user_id')
        return Message.objects.filter(
            Q(sender=user, receiver_id=other_user_id) | Q(sender_id=other_user_id, receiver=user)
        ).order_by('timestamp')

    def perform_create(self, serializer):
        receiver_id = self.kwargs.get('user_id')
        receiver = get_object_or_404(User, id=receiver_id)
        message = serializer.save(sender=self.request.user, receiver=receiver)

        # Validate if the receiver is not the same as the sender
        if message.sender == message.receiver:
            raise ValidationError({
                'receiver': [_('You cannot send a message to yourself.'),]
            })

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
        messages = self.get_queryset()
        # Mark all messages as read
        messages.filter(
            receiver=request.user,
            read=False
        ).update(read=True)
        return Response(MessageDetailSerializer(messages, many=True).data)


class ConversationListView(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(
            Q(sender=user) | Q(receiver=user)
        ).order_by('-timestamp')

    def list(self, request, *args, **kwargs):
        user = self.request.user
        messages = self.get_queryset()
        # Annotate each message with other_user_id
        annotated_messages = messages.annotate(
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
        )
        # Get the latest message ID for each other_user_id
        subquery = annotated_messages.filter(
            other_user_id=OuterRef('other_user_id')
        ).order_by('-id').values('id')[:1]
        # Get the latest message for each other_user_id
        result = annotated_messages.filter(
            id=Subquery(subquery)
        ).values(
            'other_user_id',
            'other_user_name',
            "other_user_profile_image",
            'message',
            "timestamp",
        )
        ## Query for unread message in each user_id
        '''
        # Uncomment this snippet if you want to see actual SQL query
            print(annotated_messages.query)
            return Response({
                'messages': str(result),
            })        
        '''
        chat_data = []
        for chat in result:
            chat['other_user_profile_image'] = request.build_absolute_uri(settings.MEDIA_URL + chat['other_user_profile_image'])
            chat_data.append({
                'user_id': chat['other_user_id'],
                'first_name': chat['other_user_name'],
                "profile_image": chat['other_user_profile_image'],
                'last_message': chat['message'],
                'timestamp': chat['timestamp'],
                # TODO: Update Later to boost the performance
                'unread_count': Message.objects.filter(
                    receiver=user,
                    sender_id=chat['other_user_id'],
                    read=False
                ).count()
            })
        
        # Paginate the chat summaries
        page = self.paginate_queryset(chat_data)
        if page is not None:
            return self.get_paginated_response(page)
        
        return Response(ConversationSerializer(chat_data, many=True).data)
