from .local import *

# Use in-memory channel layers for testing
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}

# Disable real Redis usage in tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Set up message consumer settings for testing
MESSAGE_CONSUMER_PING_INTERVAL = 5
MESSAGE_CONSUMER_PONG_TIMEOUT = 2
