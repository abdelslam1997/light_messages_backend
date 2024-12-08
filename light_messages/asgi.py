"""
ASGI config for light_messages project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "light_messages.settings")
django.setup()  # Setup Django first

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from light_messages.auth import JwtAuthMiddleware
from core_apps.messenger.routing import websocket_urlpatterns

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JwtAuthMiddleware(
        URLRouter(websocket_urlpatterns)
    ),
})