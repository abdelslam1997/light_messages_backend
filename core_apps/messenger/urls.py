from django.urls import path

from .views import (
    ConversationMessageListCreateView, 
    ConversationListView
)

urlpatterns = [
    # Recent conversations
    path("", ConversationListView.as_view(), name="conversation-list-view"),
    # Create a new message or list messages in a conversation
    path("<str:user_id>/messages/", ConversationMessageListCreateView.as_view(), name="conversation-list-create-view"),
]

