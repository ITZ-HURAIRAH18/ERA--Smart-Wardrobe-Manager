"""
Cloudinary utility functions for image uploads
"""
import cloudinary
import cloudinary.uploader
from django.conf import settings


def upload_image_to_cloudinary(file, folder='era-products'):
    """
    Upload an image to Cloudinary and return the URL
    
    Args:
        file: Django UploadedFile object
        folder: Cloudinary folder path
    
    Returns:
        dict with 'url' and 'public_id' or None if upload fails
    """
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type='auto',
            quality='auto',
            crop='fill',
        )
        return {
            'url': result.get('secure_url'),
            'public_id': result.get('public_id'),
        }
    except Exception as e:
        print(f"Cloudinary upload error: {e}")
        return None


def delete_image_from_cloudinary(public_id):
    """
    Delete an image from Cloudinary
    
    Args:
        public_id: Cloudinary public_id
    
    Returns:
        True if deleted, False otherwise
    """
    try:
        cloudinary.uploader.destroy(public_id)
        return True
    except Exception as e:
        print(f"Cloudinary delete error: {e}")
        return False


def get_cloudinary_url(public_id, width=None, height=None, quality='auto'):
    """
    Generate a Cloudinary URL with optional transformations
    
    Args:
        public_id: Cloudinary public_id
        width: Image width
        height: Image height
        quality: Image quality (auto, 80, etc.)
    
    Returns:
        Cloudinary URL
    """
    url = f"https://res.cloudinary.com/{settings.CLOUDINARY_CLOUD_NAME}/image/upload/"
    
    if width or height:
        transformations = f"w_{width},h_{height},c_fill,q_{quality}/"
        url += transformations
    else:
        url += f"q_{quality}/"
    
    url += public_id
    return url
