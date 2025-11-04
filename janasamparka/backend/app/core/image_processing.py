"""
Image processing utilities for media uploads
"""
from PIL import Image, ImageOps
import io
from pathlib import Path
from typing import Tuple, Optional

# Image quality settings
THUMBNAIL_SIZE = (300, 300)
MEDIUM_SIZE = (800, 800)
MAX_SIZE = (1920, 1920)
JPEG_QUALITY = 85
THUMBNAIL_QUALITY = 70


def create_thumbnail(image_bytes: bytes, size: Tuple[int, int] = THUMBNAIL_SIZE) -> bytes:
    """
    Create a thumbnail from image bytes
    """
    img = Image.open(io.BytesIO(image_bytes))
    
    # Auto-orient based on EXIF data
    img = ImageOps.exif_transpose(img)
    
    # Convert RGBA to RGB if necessary
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Create thumbnail
    img.thumbnail(size, Image.Resampling.LANCZOS)
    
    # Save to bytes
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=THUMBNAIL_QUALITY, optimize=True)
    return output.getvalue()


def optimize_image(image_bytes: bytes, max_size: Tuple[int, int] = MAX_SIZE) -> bytes:
    """
    Optimize and resize image
    """
    img = Image.open(io.BytesIO(image_bytes))
    
    # Auto-orient based on EXIF data
    img = ImageOps.exif_transpose(img)
    
    # Convert RGBA to RGB if necessary
    if img.mode == 'RGBA':
        background = Image.new('RGB', img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[3])
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize if larger than max size
    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # Save optimized
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=JPEG_QUALITY, optimize=True)
    return output.getvalue()


def get_image_dimensions(image_bytes: bytes) -> Tuple[int, int]:
    """
    Get image dimensions
    """
    img = Image.open(io.BytesIO(image_bytes))
    return img.size


def extract_exif_data(image_bytes: bytes) -> Optional[dict]:
    """
    Extract EXIF data from image (for geo-tagging, timestamp, etc.)
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif_data = img._getexif()
        
        if not exif_data:
            return None
        
        # Extract relevant EXIF tags
        exif_dict = {}
        
        # GPS coordinates (tags 34853)
        if 34853 in exif_data:
            gps_info = exif_data[34853]
            exif_dict['gps'] = gps_info
        
        # DateTime (tag 306)
        if 306 in exif_data:
            exif_dict['datetime'] = exif_data[306]
        
        # Camera make (tag 271)
        if 271 in exif_data:
            exif_dict['make'] = exif_data[271]
        
        # Camera model (tag 272)
        if 272 in exif_data:
            exif_dict['model'] = exif_data[272]
        
        return exif_dict if exif_dict else None
    
    except Exception as e:
        print(f"Error extracting EXIF data: {e}")
        return None


def is_image_file(filename: str) -> bool:
    """
    Check if file is an image based on extension
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    return Path(filename).suffix.lower() in image_extensions


def add_watermark(image_bytes: bytes, watermark_text: str = "Janasamparka") -> bytes:
    """
    Add watermark to image
    """
    from PIL import ImageDraw, ImageFont
    
    img = Image.open(io.BytesIO(image_bytes))
    
    # Create a drawing context
    draw = ImageDraw.Draw(img)
    
    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position (bottom right)
    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = (img.width - text_width - 10, img.height - text_height - 10)
    
    # Add semi-transparent watermark
    draw.text(position, watermark_text, font=font, fill=(255, 255, 255, 128))
    
    # Save
    output = io.BytesIO()
    img.save(output, format='JPEG', quality=JPEG_QUALITY)
    return output.getvalue()
