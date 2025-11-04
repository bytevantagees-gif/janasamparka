"""
Enhanced file upload service with cloud storage and optimization
"""
import os
import uuid
import hashlib
from typing import Optional, Dict, Any, List, BinaryIO
from datetime import datetime, timedelta
from pathlib import Path
from PIL import Image, ImageOps
import io
import mimetypes

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import aiofiles
import aiofiles.os

from app.core.config import settings
from app.core.logging import logger
from app.core.metrics import metrics_collector


class FileUploadService:
    """Enhanced file upload service with multiple storage backends"""
    
    def __init__(self):
        self.upload_dir = Path("uploads")
        self.upload_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.upload_dir / "media").mkdir(exist_ok=True)
        (self.upload_dir / "profile_photos").mkdir(exist_ok=True)
        (self.upload_dir / "documents").mkdir(exist_ok=True)
        
        # Initialize S3 client if configured
        self.s3_client = None
        self.s3_bucket = None
        self._init_s3()
        
        # File size limits (in bytes)
        self.max_file_sizes = {
            "image": 10 * 1024 * 1024,  # 10MB
            "video": 100 * 1024 * 1024,  # 100MB
            "audio": 20 * 1024 * 1024,   # 20MB
            "document": 5 * 1024 * 1024   # 5MB
        }
        
        # Allowed file types
        self.allowed_extensions = {
            "image": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
            "video": [".mp4", ".avi", ".mov", ".wmv", ".flv"],
            "audio": [".mp3", ".wav", ".ogg", ".m4a"],
            "document": [".pdf", ".doc", ".docx", ".txt", ".rtf"]
        }
    
    def _init_s3(self):
        """Initialize AWS S3 client"""
        try:
            if (hasattr(settings, 'AWS_ACCESS_KEY_ID') and 
                hasattr(settings, 'AWS_SECRET_ACCESS_KEY') and 
                hasattr(settings, 'AWS_S3_BUCKET')):
                
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=getattr(settings, 'AWS_REGION', 'us-east-1')
                )
                self.s3_bucket = settings.AWS_S3_BUCKET
                
                logger.info("S3 client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize S3 client", error=str(e))
    
    def _get_file_type(self, filename: str) -> str:
        """Determine file type from extension"""
        ext = Path(filename).suffix.lower()
        
        for file_type, extensions in self.allowed_extensions.items():
            if ext in extensions:
                return file_type
        
        return "unknown"
    
    def _validate_file(self, filename: str, file_size: int) -> Dict[str, Any]:
        """Validate file type and size"""
        file_type = self._get_file_type(filename)
        
        # Check file type
        if file_type == "unknown":
            return {
                "valid": False,
                "error": f"File type not allowed. Allowed types: {', '.join(self.allowed_extensions.keys())}"
            }
        
        # Check file size
        max_size = self.max_file_sizes.get(file_type, 5 * 1024 * 1024)
        if file_size > max_size:
            return {
                "valid": False,
                "error": f"File size exceeds limit of {max_size // (1024*1024)}MB for {file_type} files"
            }
        
        return {"valid": True, "file_type": file_type}
    
    def _generate_filename(self, original_filename: str, prefix: str = "") -> str:
        """Generate unique filename"""
        ext = Path(original_filename).suffix
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        
        if prefix:
            return f"{prefix}_{timestamp}_{unique_id}{ext}"
        else:
            return f"{timestamp}_{unique_id}{ext}"
    
    def _calculate_file_hash(self, file_content: bytes) -> str:
        """Calculate SHA-256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
    
    async def _optimize_image(self, file_content: bytes, filename: str) -> bytes:
        """Optimize image for web"""
        try:
            # Open image
            image = Image.open(io.BytesIO(file_content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Auto-orient image based on EXIF data
            image = ImageOps.exif_transpose(image)
            
            # Resize if too large (max 1920x1080)
            max_width, max_height = 1920, 1080
            if image.width > max_width or image.height > max_height:
                image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Optimize and save
            output = io.BytesIO()
            
            # Determine format
            ext = Path(filename).suffix.lower()
            if ext in ['.jpg', '.jpeg']:
                image.save(output, format='JPEG', quality=85, optimize=True)
            elif ext == '.png':
                image.save(output, format='PNG', optimize=True)
            elif ext == '.webp':
                image.save(output, format='WEBP', quality=85, optimize=True)
            else:
                # Default to JPEG
                image.save(output, format='JPEG', quality=85, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error("Failed to optimize image", filename=filename, error=str(e))
            return file_content
    
    async def _generate_thumbnail(self, file_content: bytes, filename: str) -> bytes:
        """Generate thumbnail for image"""
        try:
            image = Image.open(io.BytesIO(file_content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Create thumbnail (300x300)
            image.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=80, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error("Failed to generate thumbnail", filename=filename, error=str(e))
            return None
    
    async def _save_local(self, file_content: bytes, filename: str, 
                         subdirectory: str = "media") -> str:
        """Save file to local storage"""
        try:
            file_path = self.upload_dir / subdirectory / filename
            
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            return str(file_path)
            
        except Exception as e:
            logger.error("Failed to save file locally", filename=filename, error=str(e))
            raise
    
    async def _save_s3(self, file_content: bytes, filename: str, 
                      content_type: str) -> str:
        """Save file to S3 storage"""
        if not self.s3_client:
            raise Exception("S3 client not initialized")
        
        try:
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=filename,
                Body=file_content,
                ContentType=content_type,
                ACL='private',  # or 'public-read' if needed
                Metadata={
                    'upload_time': datetime.utcnow().isoformat()
                }
            )
            
            # Generate URL
            url = f"https://{self.s3_bucket}.s3.amazonaws.com/{filename}"
            
            return url
            
        except ClientError as e:
            logger.error("Failed to upload file to S3", filename=filename, error=str(e))
            raise
    
    async def upload_file(self, file_content: bytes, filename: str,
                         subdirectory: str = "media", 
                         optimize: bool = True) -> Dict[str, Any]:
        """Upload file with optimization and validation"""
        start_time = datetime.utcnow()
        
        try:
            # Validate file
            validation = self._validate_file(filename, len(file_content))
            if not validation["valid"]:
                metrics_collector.record_file_upload(
                    validation.get("file_type", "unknown"), 
                    False, len(file_content)
                )
                return {
                    "success": False,
                    "error": validation["error"]
                }
            
            file_type = validation["file_type"]
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(file_content)
            
            # Generate unique filename
            unique_filename = self._generate_filename(filename, file_type)
            
            # Optimize if it's an image
            optimized_content = file_content
            thumbnail_content = None
            
            if file_type == "image" and optimize:
                optimized_content = await self._optimize_image(file_content, filename)
                thumbnail_content = await self._generate_thumbnail(optimized_content, filename)
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = "application/octet-stream"
            
            # Save to storage
            if self.s3_client:
                # Use S3
                file_url = await self._save_s3(optimized_content, unique_filename, content_type)
                
                # Save thumbnail if generated
                thumbnail_url = None
                if thumbnail_content:
                    thumb_filename = f"thumb_{unique_filename}"
                    thumbnail_url = await self._save_s3(thumbnail_content, thumb_filename, "image/jpeg")
                
                storage_type = "s3"
            else:
                # Use local storage
                file_path = await self._save_local(optimized_content, unique_filename, subdirectory)
                file_url = f"/uploads/{subdirectory}/{unique_filename}"
                
                # Save thumbnail if generated
                thumbnail_url = None
                if thumbnail_content:
                    thumb_filename = f"thumb_{unique_filename}"
                    thumb_path = await self._save_local(thumbnail_content, thumb_filename, subdirectory)
                    thumbnail_url = f"/uploads/{subdirectory}/{thumb_filename}"
                
                storage_type = "local"
            
            # Calculate metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            original_size = len(file_content)
            final_size = len(optimized_content)
            compression_ratio = (1 - final_size / original_size) * 100 if original_size > 0 else 0
            
            # Record metrics
            metrics_collector.record_file_upload(file_type, True, final_size)
            
            result = {
                "success": True,
                "filename": unique_filename,
                "original_filename": filename,
                "file_type": file_type,
                "file_size": final_size,
                "original_size": original_size,
                "compression_ratio": round(compression_ratio, 2),
                "file_hash": file_hash,
                "content_type": content_type,
                "url": file_url,
                "thumbnail_url": thumbnail_url,
                "storage_type": storage_type,
                "upload_time": datetime.utcnow().isoformat(),
                "duration_ms": round(duration * 1000, 2)
            }
            
            logger.info("File uploaded successfully", 
                       filename=unique_filename, 
                       file_type=file_type,
                       size_kb=round(final_size / 1024, 2),
                       storage=storage_type)
            
            return result
            
        except Exception as e:
            duration = (datetime.utcnow() - start_time).total_seconds()
            metrics_collector.record_file_upload("unknown", False, len(file_content))
            
            logger.error("File upload failed", 
                        filename=filename, 
                        error=str(e),
                        duration_ms=round(duration * 1000, 2))
            
            return {
                "success": False,
                "error": f"Upload failed: {str(e)}"
            }
    
    async def delete_file(self, filename: str, storage_type: str = "local") -> bool:
        """Delete file from storage"""
        try:
            if storage_type == "s3" and self.s3_client:
                self.s3_client.delete_object(Bucket=self.s3_bucket, Key=filename)
            else:
                # Local storage
                file_path = self.upload_dir / filename
                if await aiofiles.os.path.exists(file_path):
                    await aiofiles.os.remove(file_path)
            
            logger.info("File deleted successfully", filename=filename)
            return True
            
        except Exception as e:
            logger.error("Failed to delete file", filename=filename, error=str(e))
            return False
    
    async def get_file_info(self, filename: str, storage_type: str = "local") -> Optional[Dict[str, Any]]:
        """Get file information"""
        try:
            if storage_type == "s3" and self.s3_client:
                response = self.s3_client.head_object(Bucket=self.s3_bucket, Key=filename)
                return {
                    "filename": filename,
                    "size": response.get("ContentLength", 0),
                    "last_modified": response.get("LastModified"),
                    "content_type": response.get("ContentType"),
                    "metadata": response.get("Metadata", {})
                }
            else:
                # Local storage
                file_path = self.upload_dir / filename
                if await aiofiles.os.path.exists(file_path):
                    stat = await aiofiles.os.stat(file_path)
                    return {
                        "filename": filename,
                        "size": stat.st_size,
                        "last_modified": datetime.fromtimestamp(stat.st_mtime),
                        "content_type": mimetypes.guess_type(filename)[0]
                    }
            
            return None
            
        except Exception as e:
            logger.error("Failed to get file info", filename=filename, error=str(e))
            return None
    
    async def cleanup_old_files(self, days: int = 30) -> int:
        """Clean up files older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            deleted_count = 0
            
            # Walk through upload directory
            for root, dirs, files in os.walk(self.upload_dir):
                for file in files:
                    file_path = Path(root) / file
                    
                    # Check file age
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        await aiofiles.os.remove(file_path)
                        deleted_count += 1
            
            logger.info("Old files cleaned up", deleted_count=deleted_count, days=days)
            return deleted_count
            
        except Exception as e:
            logger.error("Failed to cleanup old files", error=str(e))
            return 0


# Global file service instance
file_service = FileUploadService()
