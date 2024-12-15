import pytest
from pytest_factoryboy import register
from PIL import Image
import io
import asyncio
from channels.layers import get_channel_layer

from django.test import RequestFactory
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from core_apps.users.tests.factories import UserFactory


register(UserFactory)

@pytest.fixture
def user(db, user_factory):
    return user_factory()


@pytest.fixture
def mock_request():
    """
    Fixture that creates a mock request object for testing purposes.

    Returns:
        Callable: A function that generates mock request objects with customizable parameters.
    """
    def create_mock_request(user=None):
        """
        Creates a mock request object with an optional user object.

        Args:
            user: Optional user object to attach to the request.
            
        Returns:
            HttpRequest: A Django request object.
        """
        request = RequestFactory().get('/')
        
        # Add session middleware
        session_middleware = SessionMiddleware(get_response=lambda r: None)
        session_middleware.process_request(request)
        request.session.save()

        # Add auth middleware
        auth_middleware = AuthenticationMiddleware(get_response=lambda r: None)
        auth_middleware.process_request(request)

        # Set user explicitly
        request.user = user

        # Add build_absolute_uri method
        if not hasattr(request, 'build_absolute_uri'):
            request.build_absolute_uri = lambda x: f'http://testserver{x}'

        return request
    return create_mock_request


@pytest.fixture
def mock_image_file():
    """
    Fixture that creates a mock image file for testing purposes.
    
    Returns:
        Callable: A function that generates mock image files with customizable parameters.
    """
    def create_mock_image_file(
        size: tuple[int, int] = (100, 100),
        color: str = "red",
        format: str = "JPEG",
        content_type: str = "image/jpeg",
        filename: str = "test.jpg",
        override_file_size: int | None = None,
    ) -> SimpleUploadedFile:
        """
        Creates a mock image file with specified parameters.
        
        Args:
            size: Tuple of (width, height) for the image dimensions.
            color: Color of the image (default: "red").
            format: Image format (default: "JPEG").
            content_type: MIME type of the image (default: "image/jpeg").
            filename: Name of the generated file (default: "test.jpg").
            override_file_size: Optional size override for the file.
            
        Returns:
            SimpleUploadedFile: A Django file object containing the mock image.
        """
        image = Image.new("RGB", size, color)
        image_io = io.BytesIO()
        image.save(image_io, format)
        
        image_file = SimpleUploadedFile(
            filename,
            image_io.getvalue(),
            content_type=content_type
        )
        
        if override_file_size is not None:
            image_file.size = override_file_size
            
        return image_file

    return create_mock_image_file


@pytest.fixture(autouse=True)
async def setup_channel_layers():
    """Reset channel layers for each test"""
    channel_layers_setting = settings.CHANNEL_LAYERS
    yield
    # Clear channel layers after each test
    for channel_layer in channel_layers_setting.values():
        if "BACKEND" in channel_layer:
            try:
                layer = get_channel_layer()
                await layer.flush()
            except Exception:
                pass


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def use_test_settings(settings):
    """Force use of test settings"""
    settings.CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }
    settings.MESSAGE_CONSUMER_PING_INTERVAL = 5
    settings.MESSAGE_CONSUMER_PONG_TIMEOUT = 2