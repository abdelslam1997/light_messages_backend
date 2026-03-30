from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from .models import Message, Conversation
from .serializers import (
    MessageCreateSerializer,
    MessageDetailSerializer, 
    ConversationSerializer
)
from .paginations import (
    RecentConversationsPagination,
    ConversationMessagesPagination
)
from .utils.conversations import get_conversation_id
from .signals import messages_read


User = get_user_model()

class ConversationMessageListCreateView(generics.ListCreateAPIView):
    ''' List or Create messages View ( for a specific conversation ) '''
    serializer_class = MessageCreateSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ConversationMessagesPagination

    def get_queryset(self):
        conversation_id = get_conversation_id(
            self.request.user.id,
            self.kwargs.get('user_id')
        )
        return Message.objects.filter(
            conversation_id=conversation_id
        ).order_by('-timestamp')

    def perform_create(self, serializer):
        receiver_id = self.kwargs.get('user_id')
        receiver = get_object_or_404(User, id=receiver_id)
        if receiver.id == self.request.user.id:
            raise ValidationError({
                'receiver': [_('You cannot send a message to yourself.'),]
            })        
        serializer.save(sender=self.request.user, receiver=receiver)
        # Mark previous messages from receiver as read
        self.emit_read_signal(receiver_id, self.request.user.id, self.get_queryset())

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        sender_id = self.kwargs.get('user_id')
        reader_id = request.user.id
        self.emit_read_signal(sender_id, reader_id, queryset)
        queryset = self.paginate_queryset(queryset)
        serializer = MessageDetailSerializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)
    
    def emit_read_signal(self, sender_id, reader_id, queryset) -> bool:
        ''' Mark unread messages as read and emit signal + update Conversation. '''
        conv_id = get_conversation_id(sender_id, reader_id)
        p1_id = min(int(sender_id), int(reader_id))
        reader_is_p1 = int(reader_id) == p1_id
        unread_field = 'unread_count_p1' if reader_is_p1 else 'unread_count_p2'

        # Skip the expensive message scan when the conversation has no unreads
        has_unreads = (
            Conversation.objects
            .filter(conversation_id=conv_id, **{f'{unread_field}__gt': 0})
            .exists()
        )
        if not has_unreads:
            return False

        read_updated_qs = queryset.filter(sender_id=sender_id, read=False)
        last_message_id = read_updated_qs.values_list('id', flat=True).first()
        if last_message_id is None:
            return False

        read_updated_qs.update(read=True)
        Conversation.objects.filter(conversation_id=conv_id).update(**{unread_field: 0})

        messages_read.send(
            sender=self.__class__,
            reader_id=reader_id,
            sender_id=sender_id,
            last_message_id=last_message_id
        )
        return True


class ConversationListView(generics.ListAPIView):
    ''' List recent conversations View '''
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = RecentConversationsPagination

    def get_queryset(self):
        user = self.request.user
        return (
            Conversation.objects
            .filter(Q(participant_1=user) | Q(participant_2=user))
            .select_related('participant_1', 'participant_2')
            .only(
                'conversation_id', 'last_message_text', 'last_message_timestamp',
                'unread_count_p1', 'unread_count_p2',
                'participant_1__id', 'participant_1__first_name', 'participant_1__profile_image',
                'participant_2__id', 'participant_2__first_name', 'participant_2__profile_image',
            )
            .order_by('-last_message_timestamp')
        )