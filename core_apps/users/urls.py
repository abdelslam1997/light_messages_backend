from django.urls import path

from core_apps.users.views import (
    UserRegistrationView,
    UserRetrieveView,
    UserSearchView,
)


urlpatterns = [
    path("", UserRegistrationView.as_view(), name="user-registration"),
    path("me/", UserRetrieveView.as_view(), name="user-retrieve"),
    path("search/", UserSearchView.as_view(), name="user-search"),
]
