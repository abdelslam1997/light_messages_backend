import pytest
from pytest_factoryboy import register
from PIL import Image
import io

from django.test import RequestFactory
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.files.uploadedfile import SimpleUploadedFile

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