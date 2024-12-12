from .base import *  # noqa
from .base import env
import os


# Development specific settings should be added here

# Ensure these directories are created and writable
os.makedirs(STATIC_ROOT, exist_ok=True)
os.makedirs(MEDIA_ROOT, exist_ok=True)