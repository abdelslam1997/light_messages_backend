from django.urls import path

from core_apps.users.views import (
    UserRegistrationView,
    UserListView,
)


urlpatterns = [
    path("", UserRegistrationView.as_view(), name="user-registration"),
    path("list/", UserListView.as_view(), name="user-list"),
]
