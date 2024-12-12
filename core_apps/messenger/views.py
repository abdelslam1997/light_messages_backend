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
from .signals import messages_read


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
        last_message = read_updated_qs.first()
        if last_message is None:
            return False
        # Mark all previous messages as read
        read_updated_qs.update(read=True)
        # Get the ID of the last message that was read
        messages_read.send(
            sender=self.__class__,
            reader_id=reader_id,
            sender_id=sender_id,
            last_message=last_message
        )
        return True


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
        # print(queryset.query)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.paginate_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return self.get_paginated_response(serializer.data)