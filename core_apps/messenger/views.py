from rest_framework import generics
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from django.db.models import Max, Prefetch, Q
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

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
from .utils.conversations import get_conversation_id
from .signals import messages_read


User = get_user_model()

class ConversationMessageListCreateView(generics.ListCreateAPIView):
    ''' List or Create messages View ( for a specific conversation ) '''
    serializer_class = MessageCreateSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ConversationMessagesPagination

    def get_queryset(self):
        # Get the conversation ID
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
        # Validate if the receiver is not the same as the sender
        if receiver.id == self.request.user.id:
            raise ValidationError({
                'receiver': [_('You cannot send a message to yourself.'),]
            })        
        serializer.save(sender=self.request.user, receiver=receiver)
        # Emit the read signal to previous messages of receiver
        self.emit_read_signal(receiver_id, self.request.user.id, self.get_queryset())

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Emit the read signal
        sender_id = self.kwargs.get('user_id')
        reader_id = request.user.id
        self.emit_read_signal(sender_id, reader_id, queryset)
        # Get the paginated queryset
        queryset = self.paginate_queryset(queryset)
        serializer = MessageDetailSerializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)
    
    def emit_read_signal(self, sender_id, reader_id, queryset) -> bool:
        ''' Emit the read signal to the sender of the messages '''
        # Prepare queryset to get the last message that was read
        read_updated_qs = queryset.filter(sender_id=sender_id, read=False)
        last_message_id = read_updated_qs.values_list('id', flat=True).first()
        if last_message_id is None:
            return False
        # Mark all previous messages as read
        read_updated_qs.update(read=True)
        # Get the ID of the last message that was read
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

        # Phase 1: Thin GROUP BY — get (conversation_id → latest msg id)
        # Uses HashAggregate, no sort, minimal data per row
        sent = dict(
            Message.objects.filter(sender=user)
            .values('conversation_id')
            .annotate(latest_id=Max('id'))
            .values_list('conversation_id', 'latest_id')
        )
        received = dict(
            Message.objects.filter(receiver=user)
            .values('conversation_id')
            .annotate(latest_id=Max('id'))
            .values_list('conversation_id', 'latest_id')
        )

        # Phase 2: Merge — keep the highest id per conversation (higher id = newer)
        msg_ids = [
            max(sent.get(cid, 0), received.get(cid, 0))
            for cid in set(sent) | set(received)
        ]

        # Phase 3: Fetch only the winning messages with slim user data
        slim_user_qs = User.objects.only('id', 'first_name', 'profile_image')
        return Message.objects.prefetch_related(
            Prefetch('sender', queryset=slim_user_qs),
            Prefetch('receiver', queryset=slim_user_qs),
        ).filter(id__in=msg_ids).order_by('-timestamp')

    def list(self, request, *args, **kwargs):
        queryset = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)