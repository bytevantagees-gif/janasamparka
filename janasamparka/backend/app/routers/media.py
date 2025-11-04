"""
Media router - File upload operations
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID, uuid4
import aiofiles
import os
from pathlib import Path

from app.core.database import get_db
from app.core.auth import require_auth, get_user_constituency_id
from app.core.image_processing import (
    optimize_image, 
    create_thumbnail, 
    is_image_file,
    extract_exif_data  # type: ignore[attr-defined]
)
from app.models.complaint import Media, MediaType, Complaint
from app.models.user import User
from app.schemas.media import MediaResponse

router = APIRouter()

# Configure upload directory
UPLOAD_DIR = Path("uploads/media")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".mp4", ".mov", ".avi"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def validate_file(file: UploadFile):
    """Validate file type and size"""
    # Check extension
    file_ext = Path(file.filename or "").suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    return file_ext


@router.post("/upload", response_model=List[MediaResponse], status_code=status.HTTP_201_CREATED)
async def upload_media(
    files: List[UploadFile] = File(...),
    complaint_id: UUID = Form(...),
    photo_type: str = Form(...),  # before, during, after, evidence
    caption: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload multiple media files (photos/videos)
    """
    # Validate photo_type
    valid_photo_types = ['before', 'during', 'after', 'evidence']
    if photo_type not in valid_photo_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid photo_type. Must be one of: {', '.join(valid_photo_types)}"
        )
    
    uploaded_media: List[Media] = []
    
    for file in files:
        # Initialize GPS variables for each file
        exif_gps_lat: Optional[float] = None
        exif_gps_lng: Optional[float] = None
        
        try:
            # Validate file
            file_ext = validate_file(file)
            
            # Generate unique filename
            unique_filename = f"{uuid4()}{file_ext}"
            file_path = UPLOAD_DIR / unique_filename
            
            # Read file contents
            contents = await file.read()
            
            # Check file size
            if len(contents) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} exceeds maximum size of 10MB"
                )
            
            # Process images (optimize and create thumbnail)
            if is_image_file(file.filename or ""):
                # Extract EXIF data before optimization (optimization may strip EXIF)
                exif_data = extract_exif_data(contents)  # type: ignore
                exif_gps_lat = None
                exif_gps_lng = None
                
                if exif_data and 'gps' in exif_data:
                    try:
                        gps_info = exif_data['gps']  # type: ignore
                        # Extract GPS coordinates from EXIF
                        # GPSInfo tag 2 = latitude, tag 4 = longitude
                        # GPSInfo tag 1 = latitude ref (N/S), tag 3 = longitude ref (E/W)
                        if 2 in gps_info and 4 in gps_info:  # type: ignore
                            # Convert from degrees, minutes, seconds to decimal
                            lat = gps_info[2]  # type: ignore
                            lat_ref = gps_info.get(1, 'N')  # type: ignore
                            lng = gps_info[4]  # type: ignore
                            lng_ref = gps_info.get(3, 'E')  # type: ignore
                            
                            # Convert to decimal
                            if isinstance(lat, (list, tuple)) and len(lat) == 3:  # type: ignore[arg-type]
                                exif_gps_lat = float(lat[0]) + float(lat[1])/60 + float(lat[2])/3600  # type: ignore
                                if lat_ref == 'S':
                                    exif_gps_lat = -exif_gps_lat
                            
                            if isinstance(lng, (list, tuple)) and len(lng) == 3:  # type: ignore[arg-type]
                                exif_gps_lng = float(lng[0]) + float(lng[1])/60 + float(lng[2])/3600  # type: ignore
                                if lng_ref == 'W':
                                    exif_gps_lng = -exif_gps_lng
                    except Exception as e:
                        print(f"Error extracting GPS from EXIF: {e}")
                
                # Optimize the main image
                contents = optimize_image(contents)
                
                # Create thumbnail
                thumbnail_filename = f"thumb_{unique_filename}"
                thumbnail_path = UPLOAD_DIR / thumbnail_filename
                thumbnail_bytes = create_thumbnail(contents)
                
                async with aiofiles.open(thumbnail_path, 'wb') as f:
                    await f.write(thumbnail_bytes)
            
            # Save main file
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(contents)
            
            # Determine media type
            if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
                media_type = MediaType.IMAGE  # type: ignore[attr-defined]
            elif file_ext in ['.mp4', '.mov', '.avi']:
                media_type = MediaType.VIDEO  # type: ignore[attr-defined]
            else:
                media_type = MediaType.DOCUMENT  # type: ignore[attr-defined]
            
            # Create media record with EXIF GPS if available
            new_media = Media(
                complaint_id=complaint_id,
                url=f"/uploads/media/{unique_filename}",
                media_type=media_type,
                photo_type=photo_type,
                caption=caption,
                lat=exif_gps_lat,
                lng=exif_gps_lng,
            )
            
            db.add(new_media)
            uploaded_media.append(new_media)
            
            # If first media has GPS and complaint doesn't, update complaint
            if exif_gps_lat and exif_gps_lng and len(uploaded_media) == 1:
                complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
                if complaint and (not complaint.lat or not complaint.lng):
                    from decimal import Decimal
                    complaint.lat = Decimal(str(exif_gps_lat))
                    complaint.lng = Decimal(str(exif_gps_lng))
                    print(f"Updated complaint {complaint_id} with GPS from photo EXIF: {exif_gps_lat}, {exif_gps_lng}")
            
        except Exception as e:
            # Clean up any uploaded files on error
            for media in uploaded_media:
                try:
                    os.remove(UPLOAD_DIR / Path(media.url).name)
                except:
                    pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error uploading file {file.filename}: {str(e)}"
            )
    
    db.commit()
    
    # Refresh all media objects
    for media in uploaded_media:
        db.refresh(media)
    
    return uploaded_media


@router.get("/complaint/{complaint_id}", response_model=List[MediaResponse])
async def get_complaint_media(
    complaint_id: UUID,
    photo_type: Optional[str] = None,
    current_user: User = Depends(require_auth),
    constituency_filter: Optional[UUID] = Depends(get_user_constituency_id),
    db: Session = Depends(get_db)
):
    """
    Get all media for a specific complaint
    Non-admin users can only access media from complaints in their constituency
    """
    # First verify the user has access to this complaint
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    # Enforce constituency access control
    if constituency_filter and complaint.constituency_id != constituency_filter:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access media from complaints in your constituency"
        )
    
    query = db.query(Media).filter(Media.complaint_id == complaint_id)
    
    if photo_type:
        query = query.filter(Media.photo_type == photo_type)
    
    media = query.all()
    return media


@router.delete("/{media_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_media(
    media_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Delete a media file
    """
    media = db.query(Media).filter(Media.id == media_id).first()
    
    if not media:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found"
        )
    
    # Delete file from filesystem
    try:
        file_path = UPLOAD_DIR / Path(media.url).name
        if file_path.exists():
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")
    
    # Delete database record
    db.delete(media)
    db.commit()
    
    return None
