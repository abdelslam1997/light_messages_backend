# views.py
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from django.db.models import Q, Max, F, Case, When, IntegerField, Count, OuterRef, Subquery, CharField
from django.contrib.auth import get_user_model

from .models import Message
from .serializers import MessageSerializer, ChatSummarySerializer, MessageDetailSerializer

User = get_user_model()


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
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

        result = annotated_messages.filter(
            id=Subquery(subquery)
        ).values(
            'other_user_id',
            'other_user_name',
            "other_user_profile_image",
            'message',
            "timestamp",
        )

        '''
        # Uncomment this snippet if you want to see actual SQL query
            print(annotated_messages.query)
            return Response({
                'messages': str(result),
            })        
        '''

        chat_data = []

        for chat in result:
            chat_data.append({
                'user_id': chat['other_user_id'],
                'first_name': chat['other_user_name'],
                "profile_image": chat['other_user_profile_image'],
                'last_message': chat['message'],
                'timestamp': chat['timestamp'],
                'unread_count': 0,
            })


        # Paginate the chat summaries
        page = self.paginate_queryset(chat_data)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(ChatSummarySerializer(chat_data, many=True).data)

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)






class MessagesDetailView(generics.RetrieveAPIView):
    serializer_class = MessageDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        other_user_id = self.kwargs.get('user_id')
        return Message.objects.filter(
            Q(sender=user, receiver_id=other_user_id) | Q(sender_id=other_user_id, receiver=user)
        ).order_by('timestamp')

    def retrieve(self, request, *args, **kwargs):
        messages = self.get_queryset()

        # Mark all messages as read
        messages.filter(
            receiver=request.user,
            read=False
        ).update(read=True)

        return Response(MessageDetailSerializer(messages, many=True).data)