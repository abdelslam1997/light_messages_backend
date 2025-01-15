import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class MessageConsumer(AsyncWebsocketConsumer):
    # Seconds between pings
    PING_INTERVAL = settings.MESSAGE_CONSUMER_PING_INTERVAL
    # How long to wait for pong response
    PONG_TIMEOUT = settings.MESSAGE_CONSUMER_PONG_TIMEOUT

    async def connect(self):
        self.user = self.scope["user"]

        if self.user.is_anonymous:
            # Close the connection if not authenticated
            await self.close()
            return

        self.user_group_name = f"user_{self.user.id}"

        # Join the user group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

        # Start sending pings
        asyncio.create_task(self.keep_connection_alive())

    async def disconnect(self, close_code):
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
            else:
                # Handle other incoming messages if needed
                pass

    async def new_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    async def read_message(self, event):
        print('read_message event received:', event)
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
                        await self.close()
                        break
                    
                    # Wait for next ping interval
                    await asyncio.sleep(max(0, self.PING_INTERVAL - self.PONG_TIMEOUT))
                except Exception as e:
                    await self.close()
                    break
        except Exception:
            await self.close()
