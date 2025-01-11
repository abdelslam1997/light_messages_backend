from .base import *  # noqa
from .base import env

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

INSTALLED_APPS += ["storages"]

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": env.str("AWS_S3_ACCESS_KEY_ID"),
            "secret_key": env.str("AWS_S3_SECRET_ACCESS_KEY"),
            "bucket_name": env.str("AWS_STORAGE_BUCKET_NAME"),
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": env.str("AWS_S3_ACCESS_KEY_ID"),
            "secret_key": env.str("AWS_S3_SECRET_ACCESS_KEY"),
            "bucket_name": env.str("AWS_STORAGE_BUCKET_NAME"),
            "location": "static",
        },
    },
}