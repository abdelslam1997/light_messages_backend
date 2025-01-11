from .base import *  # noqa
from .base import env

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

INSTALLED_APPS += ["storages"]

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "AWS_S3_ACCESS_KEY_ID": env("AWS_S3_ACCESS_KEY_ID"),
            "AWS_S3_SECRET_ACCESS_KEY": env("AWS_S3_SECRET_ACCESS_KEY"),
            "AWS_STORAGE_BUCKET_NAME": env("AWS_STORAGE_BUCKET_NAME"),
            "AWS_S3_CUSTOM_DOMAIN": f"{env('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com",
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "AWS_S3_ACCESS_KEY_ID": env("AWS_S3_ACCESS_KEY_ID"),
            "AWS_S3_SECRET_ACCESS_KEY": env("AWS_S3_SECRET_ACCESS_KEY"),
            "AWS_STORAGE_BUCKET_NAME": env("AWS_STORAGE_BUCKET_NAME"),
            "AWS_S3_CUSTOM_DOMAIN": f"{env('AWS_STORAGE_BUCKET_NAME')}.s3.amazonaws.com",
            "location": "static",
        },
    },
}