import os
from datetime import datetime
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

def validate_image_file(image):
    """Validate image file type and size."""
    # Allowed file types
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
    # 5MB maximum file size
    max_size = 5 * 1024 * 1024
    
    if not image.content_type in allowed_types:
        raise ValidationError(
            _('Invalid image format. Please use JPEG, PNG or GIF.'),
            code='invalid_image'
        )
    if image.size > max_size:
        raise ValidationError(
            _('Image file too large. Size should not exceed 5MB.'), 
            code='exceeded_size_limit'
        )

def get_profile_image_path(instance, filename):
    """Generate unique path for profile images."""
    # Get the file extension
    ext = filename.split('.')[-1]
    # Generate new filename with user_id and timestamp
    filename = f"{instance.id}_{str(datetime.now().timetz())}.{ext}"
    # Return the complete path
    return os.path.join('profile_images', filename)
