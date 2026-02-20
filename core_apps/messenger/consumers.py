import json
import asyncio
import logging
from uuid import uuid4
from channels.generic.websocket import AsyncWebsocketConsumer

from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()
logger = logging.getLogger("light_messages.websocket")

class MessageConsumer(AsyncWebsocketConsumer):
    # Seconds between pings
    PING_INTERVAL = settings.MESSAGE_CONSUMER_PING_INTERVAL
    # How long to wait for pong response
    PONG_TIMEOUT = settings.MESSAGE_CONSUMER_PONG_TIMEOUT

    async def connect(self):
        self.user = self.scope["user"]
        self.connection_id = str(uuid4())

        if self.user.is_anonymous:
            # Close the connection if not authenticated
            logger.warning(
                "websocket_auth_failed",
                extra={
                    "event": "websocket_auth_failed",
                    "connection_id": self.connection_id,
                    "path": self.scope.get("path"),
                },
            )
            await self.close()
            return

        self.user_group_name = f"user_{self.user.id}"

        # Join the user group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

        logger.info(
            "websocket_connected",
            extra={
                "event": "websocket_connected",
                "connection_id": self.connection_id,
                "user_id": self.user.id,
                "group": self.user_group_name,
                "path": self.scope.get("path"),
            },
        )

        # Start sending pings
        asyncio.create_task(self.keep_connection_alive())

    async def disconnect(self, close_code):
        logger.info(
            "websocket_disconnected",
            extra={
                "event": "websocket_disconnected",
                "connection_id": getattr(self, "connection_id", None),
                "user_id": getattr(getattr(self, "user", None), "id", None),
                "group": getattr(self, "user_group_name", None),
                "close_code": close_code,
            },
        )

        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        # Handle incoming WebSocket messages
        if text_data:
            data = json.loads(text_data)

            # Check if the message is a "pong" response
            if data.get("type") == "pong":
                self.last_pong_time = asyncio.get_event_loop().time()
                logger.debug(
                    "websocket_pong_received",
                    extra={
                        "event": "websocket_pong_received",
                        "connection_id": getattr(self, "connection_id", None),
                        "user_id": getattr(getattr(self, "user", None), "id", None),
                    },
                )
            else:
                # Handle other incoming messages if needed
                pass

    async def new_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def read_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))


    async def keep_connection_alive(self):
        """
        Periodically send a ping message to the client and 
        check if a pong is received. If not, close the connection.
        """
        try:
            self.last_pong_time = asyncio.get_event_loop().time()

            while True:
                try:
                    # Send a "ping" message
                    await self.send(text_data=json.dumps({"type": "ping"}))
                    
                    # Wait for potential pong response
                    await asyncio.sleep(self.PONG_TIMEOUT)

                    # Check time since last pong
                    current_time = asyncio.get_event_loop().time()
                    if (current_time - self.last_pong_time) > self.PONG_TIMEOUT:
                        logger.warning(
                            "websocket_ping_timeout_close",
                            extra={
                                "event": "websocket_ping_timeout_close",
                                "connection_id": getattr(self, "connection_id", None),
                                "user_id": getattr(getattr(self, "user", None), "id", None),
                                "pong_timeout_seconds": self.PONG_TIMEOUT,
                            },
                        )
                        await self.close()
                        break
                    
                    # Wait for next ping interval
                    await asyncio.sleep(max(0, self.PING_INTERVAL - self.PONG_TIMEOUT))
                except Exception:
                    logger.exception(
                        "websocket_keepalive_exception",
                        extra={
                            "event": "websocket_keepalive_exception",
                            "connection_id": getattr(self, "connection_id", None),
                            "user_id": getattr(getattr(self, "user", None), "id", None),
                        },
                    )
                    await self.close()
                    break
        except Exception:
            logger.exception(
                "websocket_keepalive_fatal_exception",
                extra={
                    "event": "websocket_keepalive_fatal_exception",
                    "connection_id": getattr(self, "connection_id", None),
                    "user_id": getattr(getattr(self, "user", None), "id", None),
                },
            )
            await self.close()
