import pytest
import asyncio
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from rest_framework_simplejwt.tokens import AccessToken
from django.conf import settings

# Import the test application instead of production
from light_messages.asgi import application


@pytest.mark.asyncio
class TestMessageConsumer:
    @pytest.fixture(autouse=True)
    async def setup_test(self):
        """Setup and cleanup for each test"""
        # Setup
        self.channel_layer = get_channel_layer()
        await self.channel_layer.flush()
        
        yield
        
        # Cleanup
        await self.channel_layer.flush()

    async def setup_communicator(self, user=None, token=None):
        """Helper method to set up WebSocket communicator"""
        if user and not token:
            # Create a valid token
            token = str(AccessToken().for_user(user))
        
        # Create the communicator with the proper path
        communicator = WebsocketCommunicator(
            application=application,
            path=f"/ws/messages/?token={token}" if token else "/ws/messages/"
        )
        
        try:
            # Add a longer timeout for connection
            connected, subprotocol = await communicator.connect(timeout=2)
            print(f"Connected: {connected}, Subprotocol: {subprotocol}")
            return connected, communicator
        except Exception as e:
            await communicator.disconnect()
            raise e

    async def teardown_communicator(self, communicator):
        """Helper method to safely disconnect communicator"""
        try:
            await communicator.disconnect()
        except asyncio.CancelledError:
            print("Communicator disconnect was cancelled")
        except BaseException as e:
            print(f"Exception during disconnect: {e}")

    @pytest.mark.django_db(transaction=True)
    async def test_authentication_required(self):
        """Test that connection is rejected without authentication"""
        connected, communicator = await self.setup_communicator()
        try:
            assert not connected
        finally:
            await self.teardown_communicator(communicator)

    @pytest.mark.django_db(transaction=True)
    async def test_successful_connection(self, user):
        """Test successful WebSocket connection with valid token"""
        connected, communicator = await self.setup_communicator(user=user)
        try:
            assert connected, "WebSocket connection failed"
        finally:
            await self.teardown_communicator(communicator)

    @pytest.mark.django_db(transaction=True)
    async def test_invalid_token(self):
        """Test connection rejection with invalid token"""
        connected, communicator = await self.setup_communicator(token="invalid_token")
        try:
            assert not connected
        finally:
            await self.teardown_communicator(communicator)

    @pytest.mark.skip_in_ci("Flaky in CI environment")
    @pytest.mark.django_db(transaction=True)
    async def test_ping_pong_mechanism(self, user):
        """Test ping/pong mechanism for keeping connection alive"""
        connected, communicator = await self.setup_communicator(user=user)
        try:
            assert connected

            # Receive ping message
            response = await communicator.receive_json_from()
            assert response["type"] == "ping"

            # Send pong response
            await communicator.send_json_to({"type": "pong"})
        finally:
            await self.teardown_communicator(communicator)

    @pytest.mark.skip_in_ci("Flaky in CI environment")
    @pytest.mark.django_db(transaction=True)
    async def test_ping_timeout(self, user):
        """Test connection closure on ping timeout"""
        connected, communicator = await self.setup_communicator(user=user)
        try:
            assert connected

            # Wait for ping and don't respond
            response = await communicator.receive_json_from()
            assert response["type"] == "ping"

            # Wait for connection to close due to timeout
            # Note: Reduced timeout for testing
            await asyncio.sleep(settings.MESSAGE_CONSUMER_PONG_TIMEOUT + 1)  # PONG_TIMEOUT + 1 second
            
            # Verify connection is closed
            with pytest.raises(TimeoutError):
                await communicator.receive_from()
        finally:
            await self.teardown_communicator(communicator)

    @pytest.mark.django_db(transaction=True)
    async def test_new_message_broadcast(self, user):
        """Test broadcasting new message to connected user"""
        connected, communicator = await self.setup_communicator(user=user)
        try:
            assert connected

            # Simulate new message event
            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                f"user_{user.id}",
                {
                    "type": "new_message",
                    "message": {
                        "id": 1,
                        "sender": 2,
                        "message": "Test message",
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                }
            )

            # Receive the broadcasted message
            response = await communicator.receive_json_from()
            if response["type"] == "ping":
                response = await communicator.receive_json_from()
            assert response["type"] == "new_message"
            assert response["message"]["message"] == "Test message"
        finally:
            await self.teardown_communicator(communicator)

    @pytest.mark.django_db(transaction=True)
    async def test_read_message_broadcast(self, user):
        """Test broadcasting read message status"""
        connected, communicator = await self.setup_communicator(user=user)
        try:
            assert connected

            # Simulate read message event
            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                f"user_{user.id}",
                {
                    "type": "read_message",
                    "message": {
                        "last_read_message_id": 1,
                        "reader_id": 2
                    }
                }
            )

            # Receive the read status message
            response = await communicator.receive_json_from()
            if response["type"] == "ping":
                response = await communicator.receive_json_from()
            assert response["type"] == "read_message"
            assert response["message"]["last_read_message_id"] == 1
        finally:
            await self.teardown_communicator(communicator)

    @pytest.mark.django_db(transaction=True)
    async def test_multiple_connections_same_user(self, user):
        """Test handling multiple connections for the same user"""
        # Create two connections for the same user
        connected1, communicator1 = await self.setup_communicator(user=user)
        connected2, communicator2 = await self.setup_communicator(user=user)
        
        try:
            assert connected1 and connected2

            # Broadcast a message
            channel_layer = get_channel_layer()
            await channel_layer.group_send(
                f"user_{user.id}",
                {
                    "type": "new_message",
                    "message": {
                        "id": 1,
                        "sender": 2,
                        "message": "Test message",
                        "timestamp": "2024-01-01T00:00:00Z"
                    }
                }
            )

            # Receive the ping messages
            response1 = await communicator1.receive_json_from()
            response2 = await communicator2.receive_json_from()
            assert response1 == response2
            # Receive the broadcasted message
            response1 = await communicator1.receive_json_from()
            response2 = await communicator2.receive_json_from()
            assert response1 == response2
        finally:
            await self.teardown_communicator(communicator1)
            await self.teardown_communicator(communicator2)

