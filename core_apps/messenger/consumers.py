import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageConsumer(AsyncWebsocketConsumer):
    PING_INTERVAL = 30   # seconds between pings
    PONG_TIMEOUT = 10    # how long to wait for pong response

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
        await self.send(text_data=json.dumps(event['message']))


    async def keep_connection_alive(self):
        """
        Periodically send a ping message to the client and 
        check if a pong is received. If not, close the connection.
        """
        self.last_pong_time = asyncio.get_event_loop().time()

        while True:
            # Send a "ping" message
            await self.send(text_data=json.dumps({"type": "ping"}))
            
            # Wait PONG_TIMEOUT seconds for a pong response
            await asyncio.sleep(self.PONG_TIMEOUT)

            # Check time since last pong
            time_since_pong = asyncio.get_event_loop().time() - self.last_pong_time
            if time_since_pong > self.PONG_TIMEOUT:
                # No pong response in time, close the connection
                await self.close()
                break
            
            # If we did get a pong in time, wait until the next ping interval
            await asyncio.sleep(self.PING_INTERVAL - self.PONG_TIMEOUT)
