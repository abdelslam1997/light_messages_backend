from .base import *  # noqa
from .base import env

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

INSTALLED_APPS += ["storages"]

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "location": "static",  # Only the prefix
        },
    },
}
