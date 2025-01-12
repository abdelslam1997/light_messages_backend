from .base import *  # noqa
from .base import env

DEBUG = False

INSTALLED_APPS += ["storages"]

# AWS S3 Base Configuration
AWS_ACCESS_KEY_ID = env.str("AWS_S3_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = env.str("AWS_S3_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = env.str("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = env.str("AWS_S3_REGION_NAME")
AWS_S3_SIGNATURE_VERSION = env.str("AWS_S3_SIGNATURE_VERSION")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"

# AWS S3 Security Settings
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = False

# Cache Settings
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=604800",
}

# Storage Configuration
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "location": "media",
            "querystring_auth": False,
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        "OPTIONS": {
            "location": "static",
            "querystring_auth": False,
        },
    },
}

# URLs Configuration
STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"