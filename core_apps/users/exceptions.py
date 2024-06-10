from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class DuplicatedEmailException(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_code = "conflict"
    default_detail = {"email": _("Email has already been used.")}

    def __init__(
        self, detail=default_detail, status_code=status_code, default_code=default_code
    ):
        """
        Pass arguments if you want to override default behaviour.\n
        status_code | default 409\n
        default_code | default forbidden\n
        default_detail | {\"email\": _(\"Email has already been used\")}\n
        """
        self.status_code = status_code
        self.detail = detail
        self.default_code = default_code
