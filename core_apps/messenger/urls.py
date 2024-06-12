from django.urls import path

from .views import MessageListCreateView, MessagesDetailView

urlpatterns = [
    path("", MessageListCreateView.as_view(), name="message-list-create"),
    path("<str:user_id>/", MessagesDetailView.as_view(), name="message-detail"),
]

