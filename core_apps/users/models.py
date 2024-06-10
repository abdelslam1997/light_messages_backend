from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from core_apps.users.managers import UserManager


class LightMessagesUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name=_("Email"), unique=True)
    first_name = models.CharField(
        verbose_name=_("First Name"), max_length=30, blank=True
    )
    last_name = models.CharField(verbose_name=_("Last Name"), max_length=30, blank=True)
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=True)
    is_staff = models.BooleanField(verbose_name=_("Is Staff"), default=False)

    date_joined = models.DateTimeField(verbose_name=_("Date Joined"), auto_now_add=True)

    profile_image = models.ImageField(
        verbose_name=_("Profile Image"),
        upload_to="profile_images/",
        blank=True,
        null=True,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name",
        "last_name",
    ]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")

    def get_full_name(self):
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.email
