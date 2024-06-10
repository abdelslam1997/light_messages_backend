from django.urls import path

from core_apps.users.views import UserRegistrationView


urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-registration"),
]
